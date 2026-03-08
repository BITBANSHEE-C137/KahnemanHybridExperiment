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

import subprocess as _subprocess

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


def _log_gradient_norms(
    model: DualProcessGPT2,
    eval_dataloader,
    config: dict,
    scaler: torch.amp.GradScaler,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
    dtype: torch.dtype,
    step: int,
    wandb_run,
) -> None:
    """Compute per-loss gradient norms at eval steps (separate forward/backward passes).

    Args:
        model: The dual-process model.
        eval_dataloader: DataLoader for eval data.
        config: Full config dict.
        scaler: Gradient scaler for mixed precision.
        optimizer: The optimizer (used for zero_grad).
        device: Torch device.
        dtype: Torch dtype for autocast.
        step: Current training step.
        wandb_run: W&B run object (or None).
    """
    train_cfg = config["training"]
    mask_token_id = train_cfg["mask_token_id"]
    min_mask_ratio = train_cfg["min_mask_ratio"]
    max_mask_ratio = train_cfg["max_mask_ratio"]

    # Get one batch from eval dataloader
    try:
        batch = next(iter(eval_dataloader)).to(device)
    except StopIteration:
        return

    model.train()  # Need gradients

    # AR gradient norm
    optimizer.zero_grad()
    with torch.autocast(device_type=device.type, dtype=dtype):
        ar_loss_only = model.compute_ar_loss(batch, batch)
    scaler.scale(ar_loss_only).backward()
    scaler.unscale_(optimizer)
    grad_norm_ar = torch.nn.utils.clip_grad_norm_(model.parameters(), float('inf')).item()

    # Diffusion gradient norm
    optimizer.zero_grad()
    with torch.autocast(device_type=device.type, dtype=dtype):
        masked_ids, mask_pos = create_mask(batch, mask_token_id, min_mask_ratio, max_mask_ratio)
        diff_loss_only = model.compute_diffusion_loss(batch, masked_ids, mask_pos)
    scaler.scale(diff_loss_only).backward()
    scaler.unscale_(optimizer)
    grad_norm_diff = torch.nn.utils.clip_grad_norm_(model.parameters(), float('inf')).item()

    # Clean up
    optimizer.zero_grad()

    grad_ratio = grad_norm_diff / max(grad_norm_ar, 1e-8)
    print(f"[grad] ar_norm: {grad_norm_ar:.2f} | diff_norm: {grad_norm_diff:.2f} | ratio: {grad_ratio:.2f}")
    if wandb_run:
        wandb_run.log({
            "grad/grad_norm_ar": grad_norm_ar,
            "grad/grad_norm_diff": grad_norm_diff,
            "grad/grad_ratio": grad_ratio,
        }, step=step)


def _run_post_training(config: dict, checkpoint_dir: Path, final_step: int) -> None:
    """Run 9-step post-training sequence: benchmarks, report, sync, shutdown.

    Every step is wrapped in try/except so failures are non-fatal.
    An explicit sub_env dict is passed to all subprocesses.

    Args:
        config: Full config dict.
        checkpoint_dir: Path to checkpoint directory.
        final_step: Final training step number.
    """
    project_dir = Path(os.environ.get("PROJECT_DIR", "/home/ubuntu/KahnemanHybridExperiment"))
    data_dir = os.environ.get("DATA_DIR", "/opt/dlami/nvme/ml-lab")
    s3_bucket = os.environ.get("S3_BUCKET", "ml-lab-004507070771/dual-system-research-data")
    fleet_id = os.environ.get("FLEET_ID", "")
    region = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
    ckpt_dir_str = os.environ.get("CHECKPOINT_DIR", str(checkpoint_dir))

    # Explicit env for all subprocesses — don't rely on inherited env
    sub_env = {
        **os.environ,
        "PROJECT_DIR": str(project_dir),
        "DATA_DIR": data_dir,
        "S3_BUCKET": s3_bucket,
        "AWS_DEFAULT_REGION": region,
        "CHECKPOINT_DIR": ckpt_dir_str,
    }

    final_ckpt = checkpoint_dir / f"step_{final_step}.pt"

    # Step 1/9: Benchmarks (LAMBADA + WikiText)
    print(f"[post-training] 1/9 Running benchmarks on {final_ckpt}...")
    try:
        if final_ckpt.exists():
            _subprocess.run(
                ["python3", "-m", "scripts.benchmark",
                 "--config", "configs/tiny.yaml",
                 "--checkpoint", str(final_ckpt)],
                cwd=str(project_dir), env=sub_env,
                timeout=1800, check=True,
            )
            print("[post-training] 1/9 Benchmarks complete.")
        else:
            print(f"[post-training] 1/9 Checkpoint {final_ckpt} not found, skipping benchmarks.")
    except Exception as e:
        print(f"[post-training] 1/9 Benchmark failed (non-fatal): {e}")

    # Step 2/9: Compare systems (escalation/speed/quality)
    print("[post-training] 2/9 Running compare_systems analysis...")
    try:
        if final_ckpt.exists():
            _subprocess.run(
                ["python3", "-m", "scripts.compare_systems",
                 "--config", "configs/tiny.yaml",
                 "--checkpoint", str(final_ckpt)],
                cwd=str(project_dir), env=sub_env,
                timeout=1200, check=True,
            )
            print("[post-training] 2/9 Compare systems complete.")
        else:
            print("[post-training] 2/9 Skipped (no checkpoint).")
    except Exception as e:
        print(f"[post-training] 2/9 Compare systems failed (non-fatal): {e}")

    # Step 3/9: Generate run report (HTML)
    print("[post-training] 3/9 Generating run report...")
    try:
        _subprocess.run(
            ["python3", "-m", "scripts.generate_run_report",
             "--data-dir", data_dir,
             "--config", "configs/tiny.yaml",
             "--output-dir", str(project_dir / "infra" / "reports" / "v3"),
             "--run-version", "v3"],
            cwd=str(project_dir), env=sub_env,
            timeout=120, check=True,
        )
        print("[post-training] 3/9 Report generated.")
    except Exception as e:
        print(f"[post-training] 3/9 Report generation failed (non-fatal): {e}")

    # Step 4/9: Final auto-sitrep
    print("[post-training] 4/9 Running final auto-sitrep...")
    try:
        _subprocess.run(
            ["python3", "auto_sitrep.py"],
            cwd=str(project_dir), env=sub_env,
            timeout=120, check=True,
        )
        print("[post-training] 4/9 Auto-sitrep complete.")
    except Exception as e:
        print(f"[post-training] 4/9 Auto-sitrep failed (non-fatal): {e}")

    # Step 5/9: Finalize cost ledger
    print("[post-training] 5/9 Finalizing cost ledger...")
    try:
        _subprocess.run(
            ["bash", str(project_dir / "cost-tracker.sh"), "finalize"],
            cwd=str(project_dir), env=sub_env,
            timeout=60,
        )
        print("[post-training] 5/9 Cost finalized.")
    except Exception as e:
        print(f"[post-training] 5/9 Cost finalize failed (non-fatal): {e}")

    # Step 6/9: Explicit S3 sync (ALL artifacts)
    print("[post-training] 6/9 Syncing all artifacts to S3...")
    sync_pairs = [
        (f"{data_dir}/checkpoints/v3/", f"s3://{s3_bucket}/checkpoints/v3/"),
        (f"{data_dir}/eval_metrics/v3/", f"s3://{s3_bucket}/eval_metrics/v3/"),
        (f"{data_dir}/benchmarks/", f"s3://{s3_bucket}/benchmarks/"),
        (f"{data_dir}/logs/", f"s3://{s3_bucket}/logs/"),
        (f"{data_dir}/cost/", f"s3://{s3_bucket}/cost/"),
    ]
    for local_path, s3_path in sync_pairs:
        try:
            if Path(local_path).exists():
                _subprocess.run(
                    ["aws", "s3", "sync", local_path, s3_path, "--region", region],
                    env=sub_env, timeout=300, check=True, capture_output=True,
                )
                print(f"[post-training] 6/9 Synced {local_path}")
            else:
                print(f"[post-training] 6/9 Skipped {local_path} (not found)")
        except Exception as e:
            print(f"[post-training] 6/9 S3 sync failed for {local_path} (non-fatal): {e}")

    # Step 7/9: Git commit + push (report + sitrep)
    print("[post-training] 7/9 Git commit + push...")
    try:
        _subprocess.run(
            ["git", "add", "infra/reports/v3/", "sitrep.md"],
            cwd=str(project_dir), env=sub_env, timeout=30,
        )
        _subprocess.run(
            ["git", "commit", "-m", f"v3 run report + sitrep (step {final_step})"],
            cwd=str(project_dir), env=sub_env, timeout=30,
        )
        _subprocess.run(
            ["git", "push"],
            cwd=str(project_dir), env=sub_env, timeout=60,
        )
        print("[post-training] 7/9 Git push complete.")
    except Exception as e:
        print(f"[post-training] 7/9 Git commit/push failed (non-fatal): {e}")

    # Step 8/9: Telegram notification (with benchmark summary)
    print("[post-training] 8/9 Sending completion Telegram...")
    _send_completion_telegram(final_step, data_dir)

    # Step 9/9: Fleet zero
    if fleet_id:
        print(f"[post-training] 9/9 Zeroing fleet {fleet_id}...")
        try:
            _subprocess.run(
                ["aws", "ec2", "modify-fleet",
                 "--fleet-id", fleet_id,
                 "--target-capacity-specification",
                 "TotalTargetCapacity=0,SpotTargetCapacity=0",
                 "--region", region],
                env=sub_env, timeout=30,
                check=True, capture_output=True,
            )
            print("[post-training] 9/9 Fleet zeroed. Instance will terminate.")
        except Exception as e:
            print(f"[post-training] 9/9 Fleet zero failed: {e}")
    else:
        print("[post-training] 9/9 No FLEET_ID set, skipping fleet shutdown.")


def _send_completion_telegram(final_step: int, data_dir: str) -> None:
    """Send training completion notification via Telegram with benchmark summary.

    Args:
        final_step: Final training step number.
        data_dir: Path to data directory containing benchmarks/cost.
    """
    try:
        import urllib.request
        import urllib.parse
        import glob as _glob
        token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
        chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
        if not token or not chat_id:
            return

        # Load latest benchmark results
        bench_summary = ""
        bench_files = sorted(_glob.glob(f"{data_dir}/benchmarks/benchmark_step_*.json"))
        if bench_files:
            try:
                with open(bench_files[-1]) as f:
                    bench = json.load(f)
                lambada_acc = bench.get("lambada", {}).get("accuracy", None)
                wikitext_ppl = bench.get("wikitext", {}).get("perplexity", None)
                if lambada_acc is not None:
                    bench_summary += f"LAMBADA acc: {lambada_acc:.1%}\n"
                if wikitext_ppl is not None:
                    bench_summary += f"WikiText PPL: {wikitext_ppl:.2f}\n"
            except Exception:
                pass

        # Load cost
        cost_summary = ""
        cost_file = f"{data_dir}/cost/cost_ledger.json"
        try:
            with open(cost_file) as f:
                ledger = json.load(f)
            total = sum(s.get("cost_usd", 0) for s in ledger.get("sessions", []))
            cost_summary = f"Total cost: ${total:.2f}\n"
        except Exception:
            pass

        report_url = "https://train.bitbanshee.com/reports/v3/"

        msg = (
            f"TRAINING COMPLETE\n"
            f"Step {final_step:,} reached.\n"
            f"{bench_summary}{cost_summary}"
            f"Report: {report_url}\n"
            f"Fleet shutdown initiated."
        )
        data = urllib.parse.urlencode({
            "chat_id": chat_id, "text": msg, "parse_mode": "Markdown"
        }).encode()
        urllib.request.urlopen(
            urllib.request.Request(
                f"https://api.telegram.org/bot{token}/sendMessage", data=data
            ), timeout=10
        )
    except Exception:
        pass


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

    # Debug: write checkpoint resolution info to a file for diagnostics
    _debug_info = [
        f"CHECKPOINT_DIR env={os.environ.get('CHECKPOINT_DIR', 'NOT SET')}",
        f"checkpoint_dir resolved={checkpoint_dir}",
        f"CHECKPOINT_S3_PREFIX={CHECKPOINT_S3_PREFIX}",
        f"checkpoint_dir contents={list(checkpoint_dir.glob('step_*.pt'))}",
        f"max_steps={train_cfg['max_steps']}, smoke_test={smoke_test}, fresh_start={fresh_start}",
    ]
    for _line in _debug_info:
        print(f"[debug] {_line}", flush=True)
    # Also write to a file the dashboard can read
    _debug_path = DATA_DIR / "trainer_debug.log"
    _debug_path.write_text("\n".join(_debug_info) + "\n")

    # Resume from checkpoint if available
    start_step = 0
    if not smoke_test and not fresh_start:
        latest_ckpt = find_latest_checkpoint(checkpoint_dir)
        _resume_msg = f"find_latest_checkpoint returned: {latest_ckpt}"
        print(f"[debug] {_resume_msg}", flush=True)
        with open(_debug_path, "a") as _df:
            _df.write(_resume_msg + "\n")
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

    _loop_msg = f"Training loop: start_step={start_step}, max_steps={max_steps}, will_run={start_step < max_steps}"
    print(f"[debug] {_loop_msg}", flush=True)
    with open(DATA_DIR / "trainer_debug.log", "a") as _df:
        _df.write(_loop_msg + "\n")

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

            # Gradient norm logging (separate forward/backward passes)
            if config["training"].get("log_gradient_norms", False):
                _log_gradient_norms(
                    model, eval_dataloader, config, scaler, optimizer,
                    device, dtype, step, wandb_run,
                )

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

    # Post-training: benchmarks, cost finalize, Telegram, fleet shutdown
    _run_post_training(config, checkpoint_dir, step)


def main() -> None:
    """CLI entry point for joint training."""
    parser = argparse.ArgumentParser(description="Joint dual-process training")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--max_steps", type=int, default=None, help="Override max training steps")
    parser.add_argument("--smoke_test", action="store_true", help="Run quick smoke test")
    parser.add_argument("--fresh_start", action="store_true", help="Ignore existing checkpoints, start from scratch")
    parser.add_argument("--checkpoint_dir", type=str, default=None, help="Override checkpoint directory (bypasses env var and config)")
    parser.add_argument("--checkpoint_s3_prefix", type=str, default=None, help="Override S3 checkpoint prefix (bypasses env var)")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    # CLI overrides for checkpoint paths (bypass AMI env vars)
    if args.checkpoint_dir:
        os.environ["CHECKPOINT_DIR"] = args.checkpoint_dir
    if args.checkpoint_s3_prefix:
        os.environ["CHECKPOINT_S3_PREFIX"] = args.checkpoint_s3_prefix
        # Force reload since s3_sync module already read the env var at import time
        import src.utils.s3_sync as _s3m
        _s3m.CHECKPOINT_S3_PREFIX = args.checkpoint_s3_prefix

    train(config, smoke_test=args.smoke_test, max_steps_override=args.max_steps, fresh_start=args.fresh_start)


if __name__ == "__main__":
    main()
