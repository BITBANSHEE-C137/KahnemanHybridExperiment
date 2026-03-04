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
import json
import os
import math
import random
import time
from pathlib import Path

import numpy as np
import torch
import yaml

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.model.masking import create_mask
from src.data.openwebtext import create_dataloader, create_eval_dataloader
from src.evaluation.evaluator import evaluate
from src.utils.s3_sync import (
    upload_checkpoint,
    upload_metrics,
    upload_training_log,
    SpotTerminationHandler,
    DATA_DIR,
    CHECKPOINT_S3_PREFIX,
)


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


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    """Find the latest checkpoint by step number, checking local then S3."""
    import subprocess as _sp

    local_ckpts = sorted(
        checkpoint_dir.glob("step_*.pt"),
        key=lambda p: int(p.stem.split("_")[1]),
    )

    s3_bucket = os.environ.get("S3_BUCKET", "ml-lab-004507070771/dual-system-research-data")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    try:
        result = _sp.run(
            ["aws", "s3", "ls", f"s3://{s3_bucket}/{CHECKPOINT_S3_PREFIX}/", "--region", region],
            capture_output=True, text=True, timeout=30,
        )
        s3_steps = set()
        for line in result.stdout.strip().split("\n"):
            if "step_" in line:
                fname = line.strip().split()[-1]
                step_num = int(fname.replace("step_", "").replace(".pt", ""))
                s3_steps.add(step_num)

        local_steps = {int(p.stem.split("_")[1]) for p in local_ckpts}
        missing = s3_steps - local_steps
        if missing:
            latest_missing = max(missing)
            s3_key = f"s3://{s3_bucket}/{CHECKPOINT_S3_PREFIX}/step_{latest_missing}.pt"
            local_dest = checkpoint_dir / f"step_{latest_missing}.pt"
            print(f"[resume] Downloading checkpoint step {latest_missing} from S3...")
            _sp.run(
                ["aws", "s3", "cp", s3_key, str(local_dest), "--region", region],
                check=True, capture_output=True, timeout=300,
            )
            local_ckpts.append(local_dest)
            local_ckpts.sort(key=lambda p: int(p.stem.split("_")[1]))
    except Exception as e:
        print(f"[resume] S3 checkpoint check failed (non-fatal): {e}")

    if local_ckpts:
        return local_ckpts[-1]
    return None


def train(
    config: dict,
    smoke_test: bool = False,
    max_steps_override: int | None = None,
    pretrained: bool = True,
    fresh_start: bool = False,
) -> None:
    """Main training loop.

    Args:
        config: Full configuration dictionary loaded from YAML.
        smoke_test: If True, use smoke_test overrides from config.
        max_steps_override: Override max_steps from CLI.
        pretrained: If True, load pretrained GPT-2 weights. If False, random init.
        fresh_start: If True, ignore existing checkpoints, start from pretrained weights.
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

    # Seed RNG for reproducibility
    seed = config.get("seed", train_cfg.get("seed", 42))
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)
    random.seed(seed)
    np.random.seed(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    print(f"RNG seed: {seed}")

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

    # Checkpoint dir (needed for resume logic below)
    checkpoint_dir = Path(os.environ.get("CHECKPOINT_DIR", train_cfg["checkpoint_dir"]))
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # Resume from checkpoint if available
    start_step = 0
    if not smoke_test and not fresh_start:
        latest_ckpt = find_latest_checkpoint(checkpoint_dir)
        if latest_ckpt is not None:
            print(f"[resume] Loading checkpoint: {latest_ckpt}")
            ckpt = torch.load(latest_ckpt, map_location=device, weights_only=False)
            model.load_state_dict(ckpt["model_state_dict"])
            optimizer.load_state_dict(ckpt["optimizer_state_dict"])
            start_step = ckpt["step"]
            print(f"[resume] Resuming from step {start_step}")
        else:
            print("[resume] No checkpoint found, starting from scratch")
    elif fresh_start:
        print("[fresh_start] Starting from pretrained weights (ignoring checkpoints)")

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

    # Eval dataloader
    eval_dataloader = create_eval_dataloader(config, smoke_test=smoke_test)
    eval_every = train_cfg["eval_every"]
    eval_steps = train_cfg["eval_steps"]
    last_eval_metrics: dict[str, float] = {}

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

    # Register spot termination handler for SIGTERM
    spot_handler = SpotTerminationHandler(checkpoint_dir)
    spot_handler.register()

    # Training log
    log_dir = DATA_DIR / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    training_log: list[dict] = []

    # Gradient scaler for mixed precision
    scaler = torch.amp.GradScaler("cuda", enabled=(dtype == torch.bfloat16))

    model.train()
    step = start_step
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
                # GPT2LMHeadModel.forward(labels=) auto-shifts internally
                ar_loss = model.compute_ar_loss(input_ids, input_ids)

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
            conf_acc = last_eval_metrics.get("conf_accuracy", 0.0)
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
            training_log.append({
                "step": step,
                "ar_loss": total_ar_loss,
                "diff_loss": total_diff_loss,
                "conf_loss": total_conf_loss,
                "lr": lr,
                "time": elapsed,
            })

        # Evaluation
        if step % eval_every == 0:
            eval_metrics = evaluate(model, eval_dataloader, config, eval_steps=eval_steps)
            last_eval_metrics = eval_metrics
            print(
                f"[eval] step: {step} | ar_ppl: {eval_metrics['ar_perplexity']:.2f} | "
                f"diff_loss: {eval_metrics['diff_loss']:.4f} | "
                f"s1_tok_acc: {eval_metrics['s1_token_accuracy']:.4f} | "
                f"conf_acc: {eval_metrics['conf_accuracy']:.4f} | "
                f"conf_ece: {eval_metrics['conf_ece']:.4f} | "
                f"conf_auroc: {eval_metrics['conf_auroc']:.4f}"
            )
            if wandb_run:
                wandb_run.log({
                    f"eval/{k}": v for k, v in eval_metrics.items()
                }, step=step)
            upload_metrics(eval_metrics, step)

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
            upload_checkpoint(ckpt_path, step)

            # Keep only the last 3 checkpoints locally (S3 has all)
            local_ckpts = sorted(
                checkpoint_dir.glob("step_*.pt"),
                key=lambda p: int(p.stem.split("_")[1]),
            )
            for old_ckpt in local_ckpts[:-3]:
                old_ckpt.unlink()
                print(f"Removed old local checkpoint: {old_ckpt.name}")

    print(f"Training complete. {step} steps in {time.time() - t0:.1f}s")

    # Finalize cost tracking on normal completion
    try:
        import subprocess as _sub
        project_dir = os.environ.get("PROJECT_DIR", "/home/ubuntu/KahnemanHybridExperiment")
        _sub.run(
            ["bash", os.path.join(project_dir, "cost-tracker.sh"), "finalize"],
            timeout=30,
            capture_output=True,
        )
        print("Cost tracker finalized")
    except Exception as e:
        print(f"Cost tracker finalize failed (non-fatal): {e}")

    # Save and upload training log
    try:
        log_path = log_dir / f"training_log_{int(time.time())}.json"
        log_path.write_text(json.dumps(training_log, indent=2))
        upload_training_log(log_path)
        print(f"Training log saved: {log_path}")
    except Exception as e:
        print(f"Failed to save training log: {e}")

    if wandb_run:
        wandb_run.finish()


def main() -> None:
    """CLI entry point for joint training."""
    parser = argparse.ArgumentParser(description="Joint dual-process training")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--max_steps", type=int, default=None, help="Override max training steps")
    parser.add_argument("--smoke_test", action="store_true", help="Run quick smoke test")
    parser.add_argument("--fresh_start", action="store_true", help="Ignore existing checkpoints, start from scratch")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    train(config, smoke_test=args.smoke_test, max_steps_override=args.max_steps, fresh_start=args.fresh_start)


if __name__ == "__main__":
    main()
