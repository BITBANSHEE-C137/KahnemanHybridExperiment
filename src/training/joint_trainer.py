"""Joint trainer: trains both System 1 (diffusion) and System 2 (AR) objectives.

This is the main entry point for training. Each step:
  1. Compute AR loss (causal, next-token prediction)
  2. Mask tokens, compute diffusion loss (bidirectional, predict masked)
  3. Compute confidence loss (did System 1 get it right?)
  4. Backprop weighted sum of all three losses

Usage:
    python -m src.training.joint_trainer --config configs/tiny.yaml
    python -m src.training.joint_trainer --config configs/tiny.yaml --max_steps 100 --smoke_test
"""

import argparse
import os
import math
import time
from pathlib import Path

import torch
import yaml

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.model.masking import create_mask
from src.data.openwebtext import create_dataloader


def get_lr(step: int, warmup_steps: int, max_steps: int, max_lr: float, min_lr: float) -> float:
    """Cosine learning rate schedule with linear warmup.

    Args:
        step: Current training step.
        warmup_steps: Number of warmup steps.
        max_steps: Total training steps.
        max_lr: Peak learning rate.
        min_lr: Minimum learning rate (cosine floor).

    Returns:
        Learning rate for the current step.
    """
    if step < warmup_steps:
        return max_lr * step / warmup_steps
    if step >= max_steps:
        return min_lr
    progress = (step - warmup_steps) / (max_steps - warmup_steps)
    return min_lr + 0.5 * (max_lr - min_lr) * (1.0 + math.cos(math.pi * progress))


def train(
    config: dict,
    smoke_test: bool = False,
    max_steps_override: int | None = None,
    pretrained: bool = True,
) -> None:
    """Main training loop.

    Args:
        config: Full configuration dictionary loaded from YAML.
        smoke_test: If True, use smoke_test overrides from config.
        max_steps_override: Override max_steps from CLI.
        pretrained: If True, load pretrained GPT-2 weights. If False, random init.
    """
    train_cfg = config["training"]

    # Apply smoke_test overrides
    if smoke_test and "smoke_test" in config:
        for k, v in config["smoke_test"].items():
            train_cfg[k] = v

    if max_steps_override is not None:
        train_cfg["max_steps"] = max_steps_override

    # Device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dtype = torch.bfloat16 if train_cfg["dtype"] == "bfloat16" and device.type == "cuda" else torch.float32

    print(f"Device: {device}, dtype: {dtype}")
    print(f"Max steps: {train_cfg['max_steps']}")

    # Model
    model = DualProcessGPT2(config, pretrained=pretrained).to(device)
    print(f"Model parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Optimizer
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=train_cfg["learning_rate"],
        weight_decay=train_cfg["weight_decay"],
        betas=(0.9, 0.95),
    )

    # Data
    dataloader = create_dataloader(config, smoke_test=smoke_test)
    data_iter = iter(dataloader)

    # W&B init (optional, skip if not available)
    wandb_run = None
    try:
        import wandb
        wandb_run = wandb.init(
            project=train_cfg.get("wandb_project", "dual-process-lm"),
            name=train_cfg.get("wandb_run_name", "tiny"),
            config=config,
        )
    except Exception:
        print("W&B not available, skipping logging")

    # Training config
    max_steps = train_cfg["max_steps"]
    grad_accum = train_cfg["gradient_accumulation_steps"]
    mask_token_id = train_cfg["mask_token_id"]
    min_mask_ratio = train_cfg["min_mask_ratio"]
    max_mask_ratio = train_cfg["max_mask_ratio"]
    ar_weight = train_cfg["ar_loss_weight"]
    diff_weight = train_cfg["diff_loss_weight"]
    conf_weight = train_cfg["conf_loss_weight"]
    log_every = train_cfg["log_every"]
    checkpoint_every = train_cfg["checkpoint_every"]
    checkpoint_dir = Path(train_cfg["checkpoint_dir"])
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Gradient scaler for mixed precision
    scaler = torch.amp.GradScaler("cuda", enabled=(dtype == torch.bfloat16))

    model.train()
    step = 0
    t0 = time.time()

    while step < max_steps:
        optimizer.zero_grad()
        total_ar_loss = 0.0
        total_diff_loss = 0.0
        total_conf_loss = 0.0

        for micro_step in range(grad_accum):
            # Get batch
            try:
                batch = next(data_iter)
            except StopIteration:
                data_iter = iter(dataloader)
                batch = next(data_iter)

            input_ids = batch.to(device)

            with torch.autocast(device_type=device.type, dtype=dtype):
                # --- System 2: AR loss ---
                # Shift: predict token t+1 from token t
                ar_labels = input_ids.clone()
                ar_labels[:, :-1] = input_ids[:, 1:]
                ar_labels[:, -1] = -100  # ignore last position
                ar_loss = model.compute_ar_loss(input_ids, ar_labels)

                # --- System 1: Diffusion loss ---
                masked_ids, mask_positions = create_mask(
                    input_ids, mask_token_id, min_mask_ratio, max_mask_ratio,
                )
                diff_loss = model.compute_diffusion_loss(input_ids, masked_ids, mask_positions)

                # --- Confidence loss ---
                logits, confidence, _ = model.forward_system1(masked_ids, mask_positions)
                conf_loss = model.compute_confidence_loss(
                    confidence, logits.detach(), input_ids, mask_positions,
                )

                # Weighted total
                loss = (ar_weight * ar_loss + diff_weight * diff_loss + conf_weight * conf_loss)
                loss = loss / grad_accum

            scaler.scale(loss).backward()
            total_ar_loss += ar_loss.item() / grad_accum
            total_diff_loss += diff_loss.item() / grad_accum
            total_conf_loss += conf_loss.item() / grad_accum

        # Gradient clipping
        scaler.unscale_(optimizer)
        torch.nn.utils.clip_grad_norm_(model.parameters(), train_cfg["max_grad_norm"])

        # LR schedule
        lr = get_lr(step, train_cfg["warmup_steps"], max_steps,
                     train_cfg["learning_rate"], train_cfg["min_learning_rate"])
        for pg in optimizer.param_groups:
            pg["lr"] = lr

        scaler.step(optimizer)
        scaler.update()

        step += 1

        # Logging
        if step % log_every == 0 or step == 1:
            elapsed = time.time() - t0
            conf_acc = 0.0  # Placeholder — computed properly during eval
            print(
                f"step: {step} | ar_loss: {total_ar_loss:.4f} | "
                f"diff_loss: {total_diff_loss:.4f} | conf_acc: {conf_acc:.4f} | "
                f"lr: {lr:.2e} | time: {elapsed:.1f}s"
            )
            if wandb_run:
                wandb_run.log({
                    "step": step,
                    "ar_loss": total_ar_loss,
                    "diff_loss": total_diff_loss,
                    "conf_loss": total_conf_loss,
                    "lr": lr,
                }, step=step)

        # Checkpoint
        if step % checkpoint_every == 0:
            ckpt_path = checkpoint_dir / f"step_{step}.pt"
            torch.save({
                "step": step,
                "model_state_dict": model.state_dict(),
                "optimizer_state_dict": optimizer.state_dict(),
                "config": config,
            }, ckpt_path)
            print(f"Saved checkpoint: {ckpt_path}")

    print(f"Training complete. {step} steps in {time.time() - t0:.1f}s")

    if wandb_run:
        wandb_run.finish()


def main() -> None:
    """CLI entry point for joint training."""
    parser = argparse.ArgumentParser(description="Joint dual-process training")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--max_steps", type=int, default=None, help="Override max training steps")
    parser.add_argument("--smoke_test", action="store_true", help="Run quick smoke test")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    train(config, smoke_test=args.smoke_test, max_steps_override=args.max_steps)


if __name__ == "__main__":
    main()
