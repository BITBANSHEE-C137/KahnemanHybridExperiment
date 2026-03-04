"""S3 upload utilities for training artifact persistence.

All operations are wrapped in try/except — S3 failures never crash training.
Uses `aws s3 cp` via subprocess for simplicity and reliability.
"""

import json
import os
import signal
import subprocess
import threading
import time
from pathlib import Path


# S3 bucket path from env, with sensible default
S3_BUCKET = os.environ.get("S3_BUCKET", "ml-lab-004507070771/dual-system-research-data")
AWS_REGION = os.environ.get("AWS_DEFAULT_REGION", "us-east-1")
DATA_DIR = Path(os.environ.get("DATA_DIR", "/opt/dlami/nvme/ml-lab"))
CHECKPOINT_S3_PREFIX = os.environ.get("CHECKPOINT_S3_PREFIX", "checkpoints")
EVAL_S3_PREFIX = os.environ.get("EVAL_S3_PREFIX", "eval_metrics")


def upload_file(local_path: str | Path, s3_key: str) -> bool:
    """Upload a single file to S3.

    Args:
        local_path: Local file path to upload.
        s3_key: S3 key (path within the bucket).

    Returns:
        True if upload succeeded, False otherwise.
    """
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
    try:
        subprocess.run(
            ["aws", "s3", "cp", str(local_path), s3_uri, "--region", AWS_REGION],
            check=True,
            capture_output=True,
            timeout=300,
        )
        return True
    except Exception as e:
        print(f"[s3_sync] Upload failed {local_path} -> {s3_uri}: {e}")
        return False


def upload_file_async(local_path: str | Path, s3_key: str) -> threading.Thread:
    """Upload a file to S3 in a background thread (non-blocking).

    Args:
        local_path: Local file path to upload.
        s3_key: S3 key (path within the bucket).

    Returns:
        The background thread (already started).
    """
    t = threading.Thread(target=upload_file, args=(local_path, s3_key), daemon=True)
    t.start()
    return t


def upload_checkpoint(checkpoint_path: str | Path, step: int) -> threading.Thread:
    """Upload a training checkpoint to S3 asynchronously.

    Args:
        checkpoint_path: Local path to the .pt checkpoint file.
        step: Training step number (used for S3 key).

    Returns:
        The background thread performing the upload.
    """
    s3_key = f"{CHECKPOINT_S3_PREFIX}/step_{step}.pt"
    print(f"[s3_sync] Uploading checkpoint step {step} to s3://{S3_BUCKET}/{s3_key}")
    return upload_file_async(checkpoint_path, s3_key)


def upload_metrics(metrics: dict, step: int) -> None:
    """Write eval metrics to JSON and upload to S3.

    Args:
        metrics: Dictionary of metric names to values.
        step: Training step number.
    """
    try:
        metrics_dir = DATA_DIR / EVAL_S3_PREFIX
        metrics_dir.mkdir(parents=True, exist_ok=True)
        local_path = metrics_dir / f"eval_step_{step}.json"

        payload = {"step": step, "timestamp": time.time(), **metrics}
        local_path.write_text(json.dumps(payload, indent=2))

        s3_key = f"{EVAL_S3_PREFIX}/eval_step_{step}.json"
        upload_file_async(local_path, s3_key)
    except Exception as e:
        print(f"[s3_sync] Failed to upload metrics for step {step}: {e}")


def upload_benchmark_results(local_path: str | Path) -> None:
    """Upload benchmark results JSON to S3.

    Args:
        local_path: Path to the benchmark results JSON file.
    """
    try:
        filename = Path(local_path).name
        s3_key = f"benchmarks/{filename}"
        print(f"[s3_sync] Uploading benchmark results to s3://{S3_BUCKET}/{s3_key}")
        upload_file(local_path, s3_key)
    except Exception as e:
        print(f"[s3_sync] Failed to upload benchmark results: {e}")


def upload_training_log(log_path: str | Path) -> None:
    """Upload training log to S3.

    Args:
        log_path: Path to the training log file.
    """
    try:
        filename = Path(log_path).name
        s3_key = f"logs/{filename}"
        upload_file(log_path, s3_key)
    except Exception as e:
        print(f"[s3_sync] Failed to upload training log: {e}")


class SpotTerminationHandler:
    """Handles SIGTERM for spot instance termination.

    Registers a SIGTERM handler that performs a final sync of all artifacts
    before the instance dies. Call register() at training start.
    """

    def __init__(self, checkpoint_dir: Path, data_dir: Path | None = None) -> None:
        self.checkpoint_dir = checkpoint_dir
        self.data_dir = data_dir or DATA_DIR
        self.terminated = False

    def register(self) -> None:
        """Register the SIGTERM signal handler."""
        signal.signal(signal.SIGTERM, self._handler)
        print("[s3_sync] Spot termination handler registered (SIGTERM)")

    def _handler(self, signum: int, frame: object) -> None:
        """SIGTERM handler: finalize cost tracking, sync all artifacts, then exit."""
        print("[s3_sync] SIGTERM received — performing final sync...")
        self.terminated = True
        self._finalize_cost_tracker()
        self._final_sync()
        print("[s3_sync] Final sync complete. Exiting.")
        raise SystemExit(0)

    def _finalize_cost_tracker(self) -> None:
        """Call cost-tracker.sh finalize to persist final session cost."""
        try:
            project_dir = os.environ.get("PROJECT_DIR", "/home/ubuntu/KahnemanHybridExperiment")
            subprocess.run(
                ["bash", os.path.join(project_dir, "cost-tracker.sh"), "finalize"],
                timeout=30,
                capture_output=True,
            )
            print("[s3_sync] Cost tracker finalized")
        except Exception as e:
            print(f"[s3_sync] Cost tracker finalize failed (non-fatal): {e}")

    def _final_sync(self) -> None:
        """Upload latest checkpoint first (most critical), then sync other dirs."""
        # Priority 1: Upload the latest checkpoint file directly (most critical)
        if self.checkpoint_dir.exists():
            ckpts = sorted(
                self.checkpoint_dir.glob("step_*.pt"),
                key=lambda p: int(p.stem.split("_")[1]),
            )
            if ckpts:
                latest = ckpts[-1]
                s3_key = f"{CHECKPOINT_S3_PREFIX}/{latest.name}"
                s3_uri = f"s3://{S3_BUCKET}/{s3_key}"
                try:
                    subprocess.run(
                        ["aws", "s3", "cp", str(latest), s3_uri, "--region", AWS_REGION],
                        check=True,
                        capture_output=True,
                        timeout=180,
                    )
                    print(f"[s3_sync] Uploaded latest checkpoint {latest.name} -> {s3_uri}")
                except Exception as e:
                    print(f"[s3_sync] Latest checkpoint upload failed: {e}")

        # Priority 2: Sync smaller artifact directories
        sync_dirs = [
            (self.data_dir / "eval_metrics", "eval_metrics"),
            (self.data_dir / "logs", "logs"),
            (self.data_dir / "benchmarks", "benchmarks"),
        ]
        for local_dir, s3_prefix in sync_dirs:
            if local_dir.exists():
                s3_uri = f"s3://{S3_BUCKET}/{s3_prefix}/"
                try:
                    subprocess.run(
                        ["aws", "s3", "sync", str(local_dir), s3_uri, "--region", AWS_REGION],
                        check=True,
                        capture_output=True,
                        timeout=60,
                    )
                    print(f"[s3_sync] Synced {local_dir} -> {s3_uri}")
                except Exception as e:
                    print(f"[s3_sync] Final sync failed for {local_dir}: {e}")
