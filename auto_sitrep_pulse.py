"""Pulse integration for auto_sitrep — write sitrep events to S3 for control plane ingestion."""

import json
import os
import subprocess
import socket
from datetime import datetime, timezone
from pathlib import Path

S3_BUCKET = os.environ.get("S3_BUCKET", "ml-lab-004507070771")
S3_PREFIX = os.environ.get("S3_PREFIX", "dual-system-research-data")
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")


def write_sitrep_event(run_id: str, step: int, metrics: dict, sitrep_md: str, summary: str) -> bool:
    """Write an immutable sitrep event to S3 for Pulse ingestion.

    Creates: training-runs/{run_id}/events/sitrep-{step}.json
    The control plane TrainingWatcher picks these up and injects Pulse events.

    Args:
        run_id: Training run UUID.
        step: Current training step (used as event identity).
        metrics: Dict of current metrics (ar_loss, diff_loss, etc.).
        sitrep_md: Full sitrep markdown text.
        summary: Short Telegram-style summary text.
    """
    event = {
        "type": "sitrep",
        "run_id": run_id,
        "step": step,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "instance_id": os.environ.get("INSTANCE_ID", socket.gethostname()),
        "metrics": metrics,
        "summary": summary,
        "sitrep_md": sitrep_md[:4000],  # Truncate to avoid bloat
    }

    tmp_path = Path(f"/tmp/sitrep-event-{step}.json")
    tmp_path.write_text(json.dumps(event, indent=2))

    s3_key = f"{S3_PREFIX}/training-runs/{run_id}/events/sitrep-{step}.json"
    s3_uri = f"s3://{S3_BUCKET}/{s3_key}"

    try:
        result = subprocess.run(
            ["aws", "s3", "cp", str(tmp_path), s3_uri, "--region", AWS_REGION],
            capture_output=True, text=True, timeout=30,
        )
        if result.returncode == 0:
            print(f"[auto_sitrep] Sitrep event written to S3: {s3_key}", file=__import__("sys").stderr)
            return True
        else:
            print(f"[auto_sitrep] S3 write failed: {result.stderr}", file=__import__("sys").stderr)
            return False
    except Exception as e:
        print(f"[auto_sitrep] S3 write error: {e}", file=__import__("sys").stderr)
        return False
