#!/usr/bin/env python3
"""
ML Training Dashboard — single-file Flask web UI.

Monitors training progress by reading log files and eval JSONs from disk.
No project-specific imports; configure the paths/regexes at the top.

Spot price: The instance role lacks ec2:DescribeSpotPriceHistory, so spot
pricing is fed externally via POST /api/spot-price or a JSON file at
/tmp/spot_price.json.  A helper one-liner is printed at startup.

Usage:
    pip install flask pyyaml
    python web_dashboard.py                # http://127.0.0.1:5000 (behind nginx)
    python web_dashboard.py --port 8080
    python web_dashboard.py --spot-token SECRET  # require token for POST /api/spot-price
"""

import argparse
import glob
import json
import os
import re
import subprocess
import sys
import time
import threading
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

import yaml
from flask import Flask, Response, jsonify, request, abort, send_from_directory

# ── Configuration ────────────────────────────────────────────────────────────
PROJECT_DIR = "/home/ubuntu/KahnemanHybridExperiment"
DATA_DIR = "/opt/dlami/nvme/ml-lab"
EVAL_DIR = os.path.join(DATA_DIR, "eval_metrics")
CONFIG_PATH = os.path.join(PROJECT_DIR, "configs/tiny.yaml")
WANDB_DIR = os.path.join(PROJECT_DIR, "wandb")
CHECKPOINT_DIR = os.environ.get("CHECKPOINT_DIR", os.path.join(DATA_DIR, "checkpoints", "v3"))
SPOT_PRICE_FILE = "/tmp/spot_price.json"
BOOTSTRAP_STATUS_FILE = "/tmp/bootstrap_status.json"
COST_LEDGER_FILE = os.path.join(DATA_DIR, "cost", "cost_ledger.json")

# Spot termination detection
_spot_termination_time = None
_spot_termination_lock = threading.Lock()

IMDS_TERMINATION_URL = "http://169.254.169.254/latest/meta-data/spot/instance-action"


def _poll_spot_termination():
    """Background thread: poll IMDS for spot termination notice every 5s."""
    global _spot_termination_time
    # Get IMDSv2 token
    try:
        req = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "300"},
        )
        tok = urllib.request.urlopen(req, timeout=2).read().decode()
    except Exception:
        tok = ""
    while True:
        try:
            req = urllib.request.Request(IMDS_TERMINATION_URL)
            if tok:
                req.add_header("X-aws-ec2-metadata-token", tok)
            resp = urllib.request.urlopen(req, timeout=2)
            if resp.status == 200:
                data = json.loads(resp.read().decode())
                with _spot_termination_lock:
                    if _spot_termination_time is None:
                        _spot_termination_time = data.get("time", datetime.now(timezone.utc).isoformat())
                        print(f"[dashboard] SPOT TERMINATION NOTICE: {data}")
                        _send_telegram_alert("SPOT TERMINATION\n"
                            "Instance will be reclaimed at " + str(data.get('time', 'unknown'))
                            + "\nCheckpoint sync in progress.")
        except Exception:
            pass
        time.sleep(5)


# Start termination poller on import
_term_thread = threading.Thread(target=_poll_spot_termination, daemon=True)
_term_thread.start()

# ── Training health monitor ──────────────────────────────────────────────────────────────
_monitor_state = {
    "last_step": 0,
    "last_step_time": 0,
    "last_stall_alert": 0,
    "last_auroc": None,
    "last_diff_loss": None,
    "completion_alerted": False,
}


def _monitor_training():
    """Background thread: monitor training health, send Telegram alerts."""
    import time as _time
    _time.sleep(120)  # Wait 2 min after boot for training to start

    while True:
        try:
            status = build_status()
            now = _time.time()
            step = status.get("current_step", 0)

            # --- Training completion detection ---
            infra = status.get("infra", {})
            if step > 0 and step >= status.get("max_steps", 50000):
                if not _monitor_state["completion_alerted"]:
                    _send_telegram_alert(
                        f"TRAINING COMPLETE\n"
                        f"Reached step {step:,} / {status.get('max_steps', 50000):,}\n"
                        f"Trainer process {'running' if infra.get('trainer_running') else 'exited'}"
                    )
                    _monitor_state["completion_alerted"] = True
                _time.sleep(60)
                continue  # Skip stall detection when training is complete

            # --- Stall detection (no progress for 15 min) ---
            if step > 0:
                if step != _monitor_state["last_step"]:
                    _monitor_state["last_step"] = step
                    _monitor_state["last_step_time"] = now
                elif _monitor_state["last_step_time"] > 0:
                    stall_duration = now - _monitor_state["last_step_time"]
                    if stall_duration > 900 and now - _monitor_state["last_stall_alert"] > 900:
                        _send_telegram_alert(
                            f"TRAINING STALL\n"
                            f"No step progress for {int(stall_duration // 60)} min\n"
                            f"Stuck at step {step:,}"
                        )
                        _monitor_state["last_stall_alert"] = now

            # --- Eval regression detection ---
            latest_eval = status.get("latest_eval")
            if latest_eval:
                auroc = latest_eval.get("conf_auroc")
                diff_loss = latest_eval.get("diff_loss")

                if auroc is not None and _monitor_state["last_auroc"] is not None:
                    drop = _monitor_state["last_auroc"] - auroc
                    if drop > 0.05:
                        _send_telegram_alert(
                            f"EVAL REGRESSION -- AUROC\n"
                            f"Drop: {_monitor_state['last_auroc']:.3f} -> {auroc:.3f} ({drop:+.3f})\n"
                            f"Step: {latest_eval.get('step', '?'):,}"
                        )

                if diff_loss is not None and _monitor_state["last_diff_loss"] is not None:
                    spike = diff_loss - _monitor_state["last_diff_loss"]
                    if spike > 0.5:
                        _send_telegram_alert(
                            f"EVAL REGRESSION -- DIFF LOSS\n"
                            f"Spike: {_monitor_state['last_diff_loss']:.2f} -> {diff_loss:.2f} (+{spike:.2f})\n"
                            f"Step: {latest_eval.get('step', '?'):,}"
                        )

                if auroc is not None:
                    _monitor_state["last_auroc"] = auroc
                if diff_loss is not None:
                    _monitor_state["last_diff_loss"] = diff_loss

            # --- Spot price spike ---
            inst = status.get("instance", {})
            spot_rate = inst.get("spot_rate")
            max_spot = float(os.environ.get("MAX_SPOT_PRICE", "0.75"))
            if spot_rate is not None and spot_rate > max_spot:
                _send_telegram_alert(
                    f"SPOT PRICE SPIKE\n"
                    f"Rate: ${spot_rate:.4f}/hr exceeds ceiling ${max_spot:.2f}/hr"
                )

            # --- Crash detection: trainer PID gone ---
            if not infra.get("trainer_running") and step > 0 and step < status.get("max_steps", 50000):
                _send_telegram_alert(
                    f"TRAINING CRASH\n"
                    f"Trainer process not found at step {step:,} / {status.get('max_steps', 50000):,}\n"
                    f"Training may have crashed."
                )
                _time.sleep(300)  # Don't spam -- wait 5 min before re-checking

        except Exception as e:
            print(f"[dashboard] monitor error: {e}", file=sys.stderr)

        _time.sleep(60)


_monitor_thread = threading.Thread(target=_monitor_training, daemon=True)
_monitor_thread.start()

# Regex for training step lines
STEP_RE = re.compile(
    r"^step:\s*(?P<step>\d+)\s*\|"
    r"\s*ar_loss:\s*(?P<ar_loss>[\d.]+)\s*\|"
    r"\s*diff_loss:\s*(?P<diff_loss>[\d.]+)\s*\|"
    r"\s*conf_acc:\s*(?P<conf_acc>[\d.]+)\s*\|"
    r"\s*lr:\s*(?P<lr>[\d.eE+-]+)\s*\|"
    r"\s*time:\s*(?P<time>[\d.]+)s"
)

# Regex for eval lines
EVAL_RE = re.compile(
    r"^\[eval\]\s*step:\s*(?P<step>\d+)\s*\|"
    r"\s*ar_ppl:\s*(?P<ar_ppl>[\d.]+)\s*\|"
    r"\s*diff_loss:\s*(?P<diff_loss>[\d.]+)\s*\|"
    r"\s*s1_tok_acc:\s*(?P<s1_tok_acc>[\d.]+)\s*\|"
    r"\s*conf_acc:\s*(?P<conf_acc>[\d.]+)\s*\|"
    r"\s*conf_ece:\s*(?P<conf_ece>[\d.]+)\s*\|"
    r"\s*conf_auroc:\s*(?P<conf_auroc>[\d.]+)"
)

SSE_INTERVAL = 10  # seconds between SSE pushes
SSE_MAX_CONNECTIONS = 10
_sse_connections = 0
_sse_lock = threading.Lock()

# On-demand pricing (USD/hr) — add entries as needed
INSTANCE_PRICES = {
    "g6.xlarge": 0.8048,
    "g6.2xlarge": 0.9776,
    "g6.4xlarge": 1.3232,
    "g6.8xlarge": 2.0144,
    "g5.xlarge": 1.006,
    "g5.2xlarge": 1.212,
    "g5.4xlarge": 1.624,
    "p4d.24xlarge": 32.7726,
}

# ── Caching layer ────────────────────────────────────────────────────────────
_cache = {}
_cache_lock = threading.Lock()


def cached(key, ttl, fn):
    """Return cached value if fresh, otherwise call fn() and cache it."""
    now = time.time()
    with _cache_lock:
        if key in _cache and now - _cache[key]["t"] < ttl:
            return _cache[key]["v"]
    val = fn()
    with _cache_lock:
        _cache[key] = {"v": val, "t": time.time()}
    return val



def _send_telegram_alert(msg):
    """Send a Telegram alert in a background thread (non-blocking)."""
    def _send():
        try:
            from auto_sitrep import send_telegram
            send_telegram(msg)
        except Exception as e:
            print(f"[dashboard] Telegram alert failed: {e}", file=sys.stderr)
    threading.Thread(target=_send, daemon=True).start()


# ── Data readers ─────────────────────────────────────────────────────────────

def find_output_log():
    """Find the W&B output.log, preferring latest-run symlink."""
    latest = os.path.join(WANDB_DIR, "latest-run", "files", "output.log")
    if os.path.isfile(latest):
        return latest
    runs = sorted(glob.glob(os.path.join(WANDB_DIR, "run-*/files/output.log")))
    return runs[-1] if runs else None


def parse_training_steps():
    log = find_output_log()
    if not log:
        return []
    steps = []
    with open(log, "r") as f:
        for line in f:
            m = STEP_RE.match(line.strip())
            if m:
                steps.append({
                    "step": int(m.group("step")),
                    "ar_loss": float(m.group("ar_loss")),
                    "diff_loss": float(m.group("diff_loss")),
                    "conf_acc": float(m.group("conf_acc")),
                    "lr": float(m.group("lr")),
                    "elapsed_s": float(m.group("time")),
                })
    return steps


def parse_eval_lines():
    log = find_output_log()
    if not log:
        return []
    evals = []
    with open(log, "r") as f:
        for line in f:
            m = EVAL_RE.match(line.strip())
            if m:
                evals.append({
                    "step": int(m.group("step")),
                    "ar_ppl": float(m.group("ar_ppl")),
                    "diff_loss": float(m.group("diff_loss")),
                    "s1_tok_acc": float(m.group("s1_tok_acc")),
                    "conf_acc": float(m.group("conf_acc")),
                    "conf_ece": float(m.group("conf_ece")),
                    "conf_auroc": float(m.group("conf_auroc")),
                })
    return evals


def read_eval_jsons():
    pattern = os.path.join(EVAL_DIR, "eval_step_*.json")
    files = sorted(glob.glob(pattern))
    results = []
    for fp in files:
        try:
            with open(fp) as f:
                results.append(json.load(f))
        except (json.JSONDecodeError, IOError):
            continue
    results.sort(key=lambda x: x.get("step", 0))
    return results


def get_gpu_stats():
    try:
        out = subprocess.check_output(
            ["nvidia-smi",
             "--query-gpu=utilization.gpu,memory.used,memory.total,temperature.gpu,power.draw,power.limit,name",
             "--format=csv,noheader,nounits"],
            timeout=5, text=True
        ).strip()
        parts = [p.strip() for p in out.split(",")]
        return {
            "gpu_util": float(parts[0]),
            "vram_used_mb": float(parts[1]),
            "vram_total_mb": float(parts[2]),
            "temp_c": float(parts[3]),
            "power_w": float(parts[4]),
            "power_limit_w": float(parts[5]),
            "name": parts[6],
        }
    except Exception:
        return None


def get_infra_status():
    def is_running(pattern):
        try:
            subprocess.check_output(["pgrep", "-f", pattern], timeout=3)
            return True
        except Exception:
            return False

    checkpoints = []
    last_checkpoint = None
    if os.path.isdir(CHECKPOINT_DIR):
        checkpoints = sorted(os.listdir(CHECKPOINT_DIR))
        # Find most recent .pt file by mtime
        pt_files = [f for f in checkpoints if f.endswith('.pt')]
        if pt_files:
            latest = max(pt_files, key=lambda f: os.path.getmtime(os.path.join(CHECKPOINT_DIR, f)))
            mtime = os.path.getmtime(os.path.join(CHECKPOINT_DIR, latest))
            from datetime import datetime, timezone
            last_checkpoint = {
                "name": latest,
                "time_utc": datetime.fromtimestamp(mtime, tz=timezone.utc).strftime("%Y-%m-%d %H:%M UTC"),
                "size_mb": round(os.path.getsize(os.path.join(CHECKPOINT_DIR, latest)) / 1e6, 1),
            }

    return {
        "trainer_running": is_running("joint_trainer"),
        "sync_running": is_running("sync-checkpoint"),
        "checkpoints": checkpoints,
        "last_checkpoint": last_checkpoint,
    }


def read_config():
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


def get_log_tail(n=20):
    log = find_output_log()
    if not log:
        return []
    try:
        with open(log, "r") as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except Exception:
        return []


def get_instance_info():
    """Get EC2 instance type, lifecycle, boot time, and AZ."""
    info = {
        "instance_type": None,
        "lifecycle": None,
        "az": None,
        "boot_time_utc": None,
        "uptime_seconds": None,
        "ondemand_price_per_hour": None,
    }
    # EC2 metadata (IMDSv2)
    try:
        token_req = urllib.request.Request(
            "http://169.254.169.254/latest/api/token",
            method="PUT",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "60"},
        )
        token = urllib.request.urlopen(token_req, timeout=2).read().decode()

        def _meta(path):
            r = urllib.request.Request(
                f"http://169.254.169.254/latest/meta-data/{path}",
                headers={"X-aws-ec2-metadata-token": token},
            )
            return urllib.request.urlopen(r, timeout=2).read().decode().strip()

        info["instance_type"] = _meta("instance-type")
        info["lifecycle"] = _meta("instance-life-cycle")  # "spot" or "on-demand"
        info["az"] = _meta("placement/availability-zone")
    except Exception:
        pass

    # Boot time
    try:
        boot_str = subprocess.check_output(["uptime", "-s"], timeout=3, text=True).strip()
        boot_dt = datetime.strptime(boot_str, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
        info["boot_time_utc"] = boot_dt.isoformat()
        info["uptime_seconds"] = max(0, (datetime.now(timezone.utc) - boot_dt).total_seconds())
    except Exception:
        pass

    # On-demand price
    itype = info["instance_type"]
    if itype and itype in INSTANCE_PRICES:
        info["ondemand_price_per_hour"] = INSTANCE_PRICES[itype]

    return info


def read_spot_price():
    """Read spot price data from the external JSON file."""
    try:
        with open(SPOT_PRICE_FILE) as f:
            return json.load(f)
    except Exception:
        return None


def write_spot_price(data):
    """Write spot price data to the JSON file."""
    with open(SPOT_PRICE_FILE, "w") as f:
        json.dump(data, f, indent=2)


def read_bootstrap_status():
    """Read bootstrap progress from the status JSON written by bootstrap.sh."""
    try:
        with open(BOOTSTRAP_STATUS_FILE) as f:
            data = json.load(f)
        # Compute total elapsed
        started = data.get("started")
        finished = data.get("finished")
        if started:
            end = finished if finished else time.time()
            data["total_elapsed_s"] = round(end - started, 1)
        return data
    except Exception:
        return None


def read_cost_ledger():
    """Read the cost ledger JSON (maintained by cost-tracker.sh)."""
    try:
        with open(COST_LEDGER_FILE) as f:
            return json.load(f)
    except Exception:
        return None


# ── Composite status builder ─────────────────────────────────────────────────

def build_status():
    steps = cached("steps", 5, parse_training_steps)
    eval_lines = cached("eval_lines", 5, parse_eval_lines)
    gpu = cached("gpu", 5, get_gpu_stats)
    infra = cached("infra", 10, get_infra_status)
    config = cached("config", 60, read_config)
    instance = cached("instance", 30, get_instance_info)
    spot_data = cached("spot", 15, read_spot_price)
    log_tail = get_log_tail(20)

    max_steps = config.get("training", {}).get("max_steps", 50000)
    warmup_steps = config.get("training", {}).get("warmup_steps", 2000)

    latest = steps[-1] if steps else None
    current_step = latest["step"] if latest else 0
    progress_pct = (current_step / max_steps * 100) if max_steps else 0

    # ETA — use steps per second from recent steps for accuracy
    eta_s = None
    sps = 0

    # Phase — reflects bootstrap, recovery, and training states
    bootstrap = cached("bootstrap", 2, read_bootstrap_status)
    if bootstrap and bootstrap.get("status") == "running":
        running_step = next(
            (s for s in bootstrap.get("steps", []) if s.get("status") == "running"),
            None,
        )
        phase = running_step["label"] if running_step else "Bootstrapping"
    elif not latest or current_step == 0:
        # Bootstrap done but no training steps yet
        phase = "Starting Training"
    else:
        phase = "Idle"

    if latest and len(steps) >= 2:
        elapsed = latest["elapsed_s"]
        # Use recent window (last 50 steps) for more accurate rate estimate
        window = steps[-50:] if len(steps) >= 50 else steps
        if len(window) >= 2:
            step_delta = window[-1]["step"] - window[0]["step"]
            time_delta = window[-1]["elapsed_s"] - window[0]["elapsed_s"]
            sps = step_delta / time_delta if time_delta > 0 else 0
        else:
            sps = current_step / elapsed if elapsed > 0 else 0
        remaining = max_steps - current_step
        eta_s = remaining / sps if sps > 0 else None
        phase = "Warmup" if current_step <= warmup_steps else "Cosine Decay"

    latest_eval = eval_lines[-1] if eval_lines else None

    # Live cost recomputation
    inst = dict(instance) if instance else {}
    now = datetime.now(timezone.utc)
    uptime_s = None
    if inst.get("boot_time_utc"):
        boot_dt = datetime.fromisoformat(inst["boot_time_utc"])
        uptime_s = max(0, (now - boot_dt).total_seconds())
        inst["uptime_seconds"] = uptime_s

    # On-demand cost
    od_rate = inst.get("ondemand_price_per_hour")
    od_cost = round(od_rate * uptime_s / 3600, 4) if od_rate and uptime_s else None

    # Spot cost — computed from price history segments
    spot_rate = None
    spot_cost = None
    if spot_data and uptime_s and inst.get("boot_time_utc"):
        spot_rate = spot_data.get("current_price")
        history = spot_data.get("price_history", [])
        if history:
            boot_ts = datetime.fromisoformat(inst["boot_time_utc"]).timestamp()
            now_ts = now.timestamp()
            # Sort by timestamp ascending
            history = sorted(history, key=lambda x: x["timestamp"])
            total = 0.0
            for i, seg in enumerate(history):
                seg_start = max(seg["timestamp"], boot_ts)
                seg_end = history[i + 1]["timestamp"] if i + 1 < len(history) else now_ts
                seg_end = min(seg_end, now_ts)
                if seg_start < seg_end:
                    total += seg["price"] * (seg_end - seg_start) / 3600
            spot_cost = round(total, 4)
        elif spot_rate:
            spot_cost = round(spot_rate * uptime_s / 3600, 4)

    # Projected totals: total_run_cost + (remaining_steps / sps * rate)
    remaining_steps = max(0, max_steps - current_step) if current_step else max_steps
    od_projected = None
    spot_projected = None
    if sps and sps > 0 and remaining_steps > 0:
        remaining_hours = remaining_steps / sps / 3600
        if od_rate:
            od_remaining_cost = od_rate * remaining_hours
            od_projected = round((od_cost or 0) + od_remaining_cost, 2)
        if spot_rate:
            spot_remaining_cost = spot_rate * remaining_hours
            spot_projected = round((spot_cost or 0) + spot_remaining_cost, 2)

    inst["ondemand_cost"] = od_cost
    inst["ondemand_projected"] = od_projected
    inst["spot_rate"] = spot_rate
    inst["spot_cost"] = spot_cost
    inst["spot_projected"] = spot_projected
    inst["spot_updated"] = spot_data.get("updated") if spot_data else None
    if od_cost and spot_cost:
        inst["savings"] = round(od_cost - spot_cost, 2)
        inst["savings_pct"] = round((1 - spot_cost / od_cost) * 100, 1)

    # Total run cost from ledger (across all spot sessions)
    ledger = cached("cost_ledger", 30, read_cost_ledger)
    sessions_breakdown = []
    total_training_time_s = None
    if ledger:
        # Use live spot_cost for current session instead of stale ledger value
        ledger_total = ledger.get("total_cost", 0)
        sessions = ledger.get("sessions", [])
        if spot_cost is not None:
            current_sess_ledger_cost = 0
            for s in sessions:
                if not s.get("finalized", False):
                    current_sess_ledger_cost = s.get("spot_cost", 0)
                    break
            inst["total_run_cost"] = round(ledger_total - current_sess_ledger_cost + spot_cost, 4)
        else:
            inst["total_run_cost"] = ledger_total
        inst["total_sessions"] = len(sessions)
        # Compute per-session durations and total training time
        total_time = 0.0
        for sess in sessions:
            boot = sess.get("boot_time")
            end = sess.get("end_time")
            duration_s = None
            if boot:
                try:
                    boot_dt = datetime.fromisoformat(boot)
                    end_dt = datetime.fromisoformat(end) if end else now
                    duration_s = max(0, (end_dt - boot_dt).total_seconds())
                    total_time += duration_s
                except (ValueError, TypeError):
                    pass
            sessions_breakdown.append({
                "instance_id": sess.get("instance_id", "?"),
                "instance_type": sess.get("instance_type", "?"),
                "az": sess.get("az", "?"),
                "boot_time": boot,
                "duration_s": duration_s,
                "steps_start": sess.get("steps_start"),
                "steps_end": sess.get("steps_end"),
                "spot_cost": sess.get("spot_cost", 0),
                "finalized": sess.get("finalized", False),
            })
        total_training_time_s = total_time if total_time > 0 else None
    else:
        inst["total_run_cost"] = spot_cost
        inst["total_sessions"] = 1 if spot_cost else 0

    # Training time — use total across all instances, not just current
    elapsed_s = latest["elapsed_s"] if latest else None
    remaining_s = round(eta_s, 0) if eta_s else None

    # Next milestones
    tcfg = config.get("training", {})
    ckpt_every = tcfg.get("checkpoint_every", 5000)
    eval_every = tcfg.get("eval_every", 1000)
    milestones = []
    if current_step > 0:
        next_eval = ((current_step // eval_every) + 1) * eval_every
        next_ckpt = ((current_step // ckpt_every) + 1) * ckpt_every
        milestones.append({"label": "next eval", "step": next_eval})
        milestones.append({"label": "next checkpoint", "step": next_ckpt})
        if current_step <= warmup_steps:
            milestones.append({"label": "warmup ends", "step": warmup_steps})
        milestones.sort(key=lambda x: x["step"])

    return {
        "timestamp": now.isoformat(),
        "current_step": current_step,
        "max_steps": max_steps,
        "progress_pct": round(progress_pct, 2),
        "phase": phase,
        "eta_seconds": remaining_s,
        "elapsed_seconds": round(elapsed_s, 0) if elapsed_s else None,
        "latest_train": latest,
        "latest_eval": latest_eval,
        "next_eval_step": ((current_step // eval_every) + 1) * eval_every if current_step > 0 and latest_eval is None else None,
        "gpu": gpu,
        "infra": infra,
        "milestones": milestones,
        "total_training_time_s": round(total_training_time_s, 0) if total_training_time_s else None,
        "sessions_breakdown": sessions_breakdown,
        "instance": inst,
        "cost_controls": {
            "max_budget": float(os.environ.get("MAX_BUDGET", 50)),
            "max_spot_price": float(os.environ.get("MAX_SPOT_PRICE", 0.75)),
            "fleet_id": os.environ.get("FLEET_ID", ""),
        },
        "bootstrap": cached("bootstrap", 2, read_bootstrap_status),
        "spot_termination": _spot_termination_time,
        "log_tail": log_tail,
        "config_summary": {
            "model": config.get("model", {}).get("name", "?"),
            "batch_size": tcfg.get("batch_size"),
            "grad_accum": tcfg.get("gradient_accumulation_steps"),
            "lr": tcfg.get("learning_rate"),
            "warmup_steps": warmup_steps,
            "max_steps": max_steps,
            "checkpoint_every": ckpt_every,
            "eval_every": eval_every,
        },
    }


# ── Flask app ─────────────────────────────────────────────────────────────────

app = Flask(__name__)


@app.route("/favicon.ico")
def favicon():
    return app.send_static_file("favicon.ico")

@app.route("/reports/<path:path>")
def serve_report(path: str):
    reports_dir = Path(__file__).parent / "infra" / "reports"
    return send_from_directory(str(reports_dir), path)

@app.route("/api/status")
def api_status():
    return jsonify(build_status())


@app.route("/api/cost/total")
def api_cost_total():
    ledger = read_cost_ledger()
    if ledger:
        return jsonify(ledger)
    return jsonify({"error": "no cost ledger"}), 404


@app.route("/api/history")
def api_history():
    steps = cached("steps", 5, parse_training_steps)
    return jsonify(steps)


@app.route("/api/eval/history")
def api_eval_history():
    eval_jsons = cached("eval_jsons", 15, read_eval_jsons)
    eval_lines = cached("eval_lines", 5, parse_eval_lines)
    seen = {e.get("step") for e in eval_jsons}
    merged = list(eval_jsons)
    for e in eval_lines:
        if e["step"] not in seen:
            merged.append(e)
    merged.sort(key=lambda x: x.get("step", 0))
    return jsonify(merged)


@app.route("/api/spot-price", methods=["GET"])
def api_spot_price_get():
    data = read_spot_price()
    if data:
        return jsonify(data)
    return jsonify({"error": "no spot price data"}), 404


@app.route("/api/spot-price", methods=["POST"])
def api_spot_price_post():
    """Accept spot price data from an external source (e.g. local AWS CLI).

    Requires Authorization: Bearer <token> header when --spot-token is set.

    Expected JSON:
    {
      "current_price": 0.3765,
      "az": "us-east-1b",
      "updated": "2026-02-28T16:00:00Z",
      "price_history": [
        {"timestamp": 1740700000, "price": 0.3771},
        {"timestamp": 1740720000, "price": 0.3765}
      ]
    }
    """
    # Token auth
    if app.config.get("SPOT_TOKEN"):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer ") or auth[7:] != app.config["SPOT_TOKEN"]:
            abort(403)

    # Payload size guard (redundant with nginx, but defense-in-depth)
    if request.content_length and request.content_length > 100_000:
        return jsonify({"error": "payload too large"}), 413

    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        return jsonify({"error": "invalid JSON"}), 400

    # Validate required field
    cp = data.get("current_price")
    if cp is None:
        return jsonify({"error": "missing current_price"}), 400
    try:
        cp = float(cp)
    except (TypeError, ValueError):
        return jsonify({"error": "current_price must be a number"}), 400
    if not (0 < cp < 1000):
        return jsonify({"error": "current_price out of range"}), 400
    data["current_price"] = cp

    # Validate optional price_history
    history = data.get("price_history")
    if history is not None:
        if not isinstance(history, list):
            return jsonify({"error": "price_history must be a list"}), 400
        for entry in history:
            if not isinstance(entry, dict):
                return jsonify({"error": "price_history entries must be objects"}), 400
            if "timestamp" not in entry or "price" not in entry:
                return jsonify({"error": "price_history entries need timestamp and price"}), 400
            try:
                entry["timestamp"] = float(entry["timestamp"])
                entry["price"] = float(entry["price"])
            except (TypeError, ValueError):
                return jsonify({"error": "invalid types in price_history"}), 400

    data["updated"] = data.get("updated", datetime.now(timezone.utc).isoformat())
    write_spot_price(data)
    # Bust cache
    with _cache_lock:
        _cache.pop("spot", None)
    return jsonify({"ok": True})


@app.route("/stream")
def stream():
    global _sse_connections
    with _sse_lock:
        if _sse_connections >= SSE_MAX_CONNECTIONS:
            return jsonify({"error": "too many SSE connections"}), 429
        _sse_connections += 1

    def generate():
        global _sse_connections
        try:
            while True:
                data = json.dumps(build_status())
                yield f"data: {data}\n\n"
                time.sleep(SSE_INTERVAL)
        finally:
            with _sse_lock:
                _sse_connections -= 1

    return Response(generate(), mimetype="text/event-stream",
                    headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})


SITREP_FILE = os.path.join(PROJECT_DIR, "sitrep.md")


@app.route("/api/debug")
def api_debug():
    debug_file = os.path.join(DATA_DIR, "trainer_debug.log")
    if not os.path.isfile(debug_file):
        return jsonify({"content": "No debug log yet"})
    with open(debug_file) as f:
        return jsonify({"content": f.read()})


@app.route("/api/sitrep")
def api_sitrep():
    if not os.path.isfile(SITREP_FILE):
        return jsonify({"content": "_No sitrep available yet._", "modified": None})
    mtime = os.path.getmtime(SITREP_FILE)
    modified = datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()
    with open(SITREP_FILE) as f:
        text = f.read()
    return jsonify({"content": text, "modified": modified})


# ── Telegram webhook ──────────────────────────────────────────────────────────

_command_cooldowns = {}
_cooldown_lock = threading.Lock()


def _check_cooldown(command: str, seconds: int) -> bool:
    """Return True if command is still on cooldown."""
    now = time.time()
    with _cooldown_lock:
        last = _command_cooldowns.get(command, 0)
        if now - last < seconds:
            return True
        _command_cooldowns[command] = now
        return False


def _send_telegram_reply(chat_id: str, text: str, parse_mode: str = "Markdown") -> None:
    """Send a reply to a specific Telegram chat_id."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    if not token:
        return
    if len(text) > 4000:
        text = text[:3990] + "\n...(truncated)"
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode,
    }).encode()
    try:
        req = urllib.request.Request(url, data=data)
        urllib.request.urlopen(req, timeout=15)
    except Exception as e:
        print(f"[dashboard] Telegram reply failed: {e}", file=sys.stderr)


def _handle_status_command(chat_id: str) -> None:
    """Handle /status — quick inline metrics."""
    if _check_cooldown("status", 15):
        _send_telegram_reply(chat_id, "Status on cooldown (15s). Try again shortly.")
        return
    try:
        s = build_status()
        step = s.get("current_step", 0)
        max_steps = s.get("max_steps", 50000)
        pct = s.get("progress_pct", 0)
        gpu = s.get("gpu") or {}
        inst = s.get("instance") or {}
        le = s.get("latest_eval") or {}
        eta_s = s.get("eta_seconds")
        eta_h = eta_s / 3600 if eta_s else 0

        total_cost = inst.get("total_run_cost") or inst.get("spot_cost") or 0

        lines = [
            f"Step {step:,}/{max_steps//1000}k ({pct:.0f}%)",
            f"GPU: {gpu.get('gpu_util', 0):.0f}% | {gpu.get('vram_used_mb', 0)/1024:.1f}/{gpu.get('vram_total_mb', 0)/1024:.0f}GB | {gpu.get('temp_c', 0):.0f}C",
            f"ETA: ~{eta_h:.0f}h",
            f"AR PPL: {le.get('ar_ppl', 0):.1f} | Diff: {le.get('diff_loss', 0):.2f} | S1: {le.get('s1_tok_acc', 0)*100:.1f}%",
            f"AUROC: {le.get('conf_auroc', 0):.3f} | ECE: {le.get('conf_ece', 0):.4f}",
            f"Cost: ${total_cost:.2f} / $50 budget",
        ]
        _send_telegram_reply(chat_id, "\n".join(lines), parse_mode="")
    except Exception as e:
        _send_telegram_reply(chat_id, f"Error fetching status: {e}", parse_mode="")


def _handle_sitrep_command(chat_id: str) -> None:
    """Handle /sitrep — acknowledge, run sitrep, report errors."""
    if _check_cooldown("sitrep", 60):
        _send_telegram_reply(chat_id, "Sitrep on cooldown (60s). Try again shortly.")
        return
    _send_telegram_reply(chat_id, "Generating sitrep...", parse_mode="")

    def _run():
        try:
            env = dict(os.environ)
            result = subprocess.run(
                ["python3", "auto_sitrep.py", "--force-telegram"],
                cwd=PROJECT_DIR,
                env=env,
                capture_output=True,
                text=True,
                timeout=120,
            )
            # Log output for debugging
            with open("/tmp/auto-sitrep-manual.log", "a") as f:
                f.write(result.stdout)
                if result.stderr:
                    f.write(result.stderr)
            if result.returncode != 0:
                err_tail = (result.stderr or result.stdout or "unknown error")[-500:]
                _send_telegram_reply(
                    chat_id,
                    f"Sitrep generation failed (rc={result.returncode}):\n{err_tail}",
                    parse_mode="",
                )
        except subprocess.TimeoutExpired:
            _send_telegram_reply(chat_id, "Sitrep generation timed out (120s).", parse_mode="")
        except Exception as e:
            _send_telegram_reply(chat_id, f"Failed to launch sitrep: {e}", parse_mode="")

    threading.Thread(target=_run, daemon=True).start()


def _handle_help_command(chat_id: str) -> None:
    """Handle /help — list available commands."""
    text = (
        "Available commands:\n"
        "/status — Quick training status (15s cooldown)\n"
        "/sitrep — Full sitrep with metrics image (60s cooldown)\n"
        "/help — This message"
    )
    _send_telegram_reply(chat_id, text, parse_mode="")


_COMMAND_HANDLERS = {
    "/status": _handle_status_command,
    "/sitrep": _handle_sitrep_command,
    "/help": _handle_help_command,
}


@app.route("/api/telegram/webhook", methods=["POST"])
def telegram_webhook():
    """Receive Telegram bot updates via webhook."""
    # Validate secret token header
    secret = app.config.get("TELEGRAM_WEBHOOK_SECRET", "")
    if secret:
        header_secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token", "")
        if header_secret != secret:
            abort(403)

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"ok": True})

    message = data.get("message", {})
    chat_id = str(message.get("chat", {}).get("id", ""))
    text = (message.get("text") or "").strip()

    # Only respond to configured chat
    expected_chat = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not chat_id or chat_id != expected_chat:
        return jsonify({"ok": True})

    # Parse command (strip @botname suffix)
    command = text.split()[0].split("@")[0].lower() if text else ""

    handler = _COMMAND_HANDLERS.get(command)
    if handler:
        threading.Thread(target=handler, args=(chat_id,), daemon=True).start()

    return jsonify({"ok": True})


@app.route("/")
def index():
    from flask import make_response
    resp = make_response(HTML_PAGE)
    resp.headers["Cache-Control"] = "no-cache, max-age=0, must-revalidate"
    return resp


# ── Inline HTML/CSS/JS ────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dual-Process Language Model — Dashboard</title>
<link rel="icon" type="image/x-icon" href="/static/favicon.ico">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4/dist/chart.umd.min.js"></script>
<style>
:root {
  --bg: #0f1117;
  --surface: #1a1d27;
  --border: #2a2d3a;
  --text: #e0e0e0;
  --dim: #888;
  --accent: #60a5fa;
  --green: #34d399;
  --yellow: #fbbf24;
  --red: #f87171;
  --orange: #fb923c;
}
*, *::before, *::after { margin: 0; padding: 0; box-sizing: border-box; }
html { overflow-x: hidden; }
body {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--bg);
  background-image: url('/static/hero.png');
  background-size: cover;
  background-position: center top;
  background-repeat: no-repeat;
  background-attachment: fixed;
  color: var(--text);
  font-size: 17px;
  line-height: 1.5;
  overflow-x: hidden;
  min-width: 0;
}
body::before {
  content: '';
  position: fixed;
  inset: 0;
  background: rgba(15, 17, 23, 0.88);
  z-index: 0;
  pointer-events: none;
}
.container { position: relative; z-index: 1; }
.container {
  max-width: 1080px;
  margin: 0 auto;
  padding: 12px;
  overflow: hidden;
}

/* Header */
.header {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  padding: 60px 14px 12px;
  background: url('/hero.png') center -75px / cover no-repeat;
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 12px;
  gap: 6px;
  position: relative;
}
.header::before {
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 17, 23, 0.65);
  border-radius: inherit;
}
.header > * {
  position: relative;
  z-index: 1;
}
.header h1 { font-size: 22px; font-weight: 600; white-space: nowrap; }
.header-sub { display: flex; align-items: center; gap: 16px; flex-wrap: wrap; width: 100%; justify-content: space-between; }
.header .meta { color: var(--dim); font-size: 14px; }
.header-links { display: flex; gap: 8px; font-size: 13px; }
.header-links a {
  color: var(--text);
  text-decoration: none;
  white-space: nowrap;
  padding: 3px 10px;
  border: 1px solid var(--border);
  border-radius: 6px;
  background: var(--bg);
  transition: border-color 0.2s, background 0.2s;
}
.header-links a:hover {
  border-color: var(--accent);
  background: rgba(232, 121, 84, 0.1);
}
.sitrep-badge {
  background: rgba(167, 139, 250, 0.08);
  border-color: rgba(167, 139, 250, 0.3);
  color: #a78bfa;
  animation: breathe 3s ease-in-out infinite;
}
.sitrep-badge:hover {
  background: rgba(167, 139, 250, 0.18);
  border-color: #a78bfa;
}
.sitrep-badge::before {
  content: '';
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #a78bfa;
  margin-right: 6px;
  vertical-align: middle;
}
@keyframes breathe {
  0%, 100% { border-color: rgba(167, 139, 250, 0.3); box-shadow: 0 0 0 0 rgba(167, 139, 250, 0); }
  50% { border-color: #a78bfa; box-shadow: 0 0 8px rgba(167, 139, 250, 0.15); }
}
.sitrep-badge-fresh {
  background: rgba(248, 113, 113, 0.08);
  border-color: rgba(248, 113, 113, 0.3);
  color: #f87171;
  animation: breathe-red 3s ease-in-out infinite;
}
.sitrep-badge-fresh:hover {
  background: rgba(248, 113, 113, 0.18);
  border-color: #f87171;
}
.sitrep-badge-fresh::before {
  content: '';
  display: inline-block;
  width: 6px; height: 6px;
  border-radius: 50%;
  background: #f87171;
  margin-right: 6px;
  vertical-align: middle;
}
@keyframes breathe-red {
  0%, 100% { border-color: rgba(248, 113, 113, 0.3); box-shadow: 0 0 0 0 rgba(248, 113, 113, 0); }
  50% { border-color: #f87171; box-shadow: 0 0 8px rgba(248, 113, 113, 0.15); }
}
.pulse {
  display: inline-block;
  width: 8px; height: 8px;
  border-radius: 50%;
  background: var(--green);
  margin-right: 6px;
  animation: pulse 2s infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.3; }
}

/* Grid */
.grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

/* Cards */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  min-width: 0;
  overflow: hidden;
}
.card-full { margin-bottom: 12px; }
.card h2 {
  font-size: 15px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--dim);
  margin-bottom: 10px;
}

/* Progress bar */
.progress-outer {
  width: 100%;
  height: 22px;
  background: var(--bg);
  border-radius: 4px;
  overflow: hidden;
  margin: 6px 0;
}
.progress-inner {
  height: 100%;
  background: linear-gradient(90deg, var(--accent), var(--green));
  border-radius: 4px;
  transition: width 0.5s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 15px;
  font-weight: 600;
  color: #000;
  min-width: 36px;
}

/* Metric boxes */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(130px, 1fr));
  gap: 8px;
}
.metric-box {
  background: var(--bg);
  border-radius: 6px;
  padding: 10px 8px;
  text-align: center;
  min-width: 0;
  overflow: hidden;
  border-left: 3px solid transparent;
  transition: border-color 0.4s, color 0.4s;
}
.metric-box.rag-green { border-left-color: var(--green); }
.metric-box.rag-green .value { color: var(--green); }
.metric-box.rag-amber { border-left-color: var(--yellow); }
.metric-box.rag-amber .value { color: var(--yellow); }
.metric-box.rag-red { border-left-color: var(--red); }
.metric-box.rag-red .value { color: var(--red); }
.metric-box .label {
  font-size: 13px;
  color: var(--dim);
  margin-bottom: 3px;
}
.metric-box .value {
  font-size: 20px;
  font-weight: 700;
  white-space: nowrap;
}
.metric-box .sub { font-size: 13px; color: var(--dim); margin-top: 2px; }
.metric-box canvas { margin-top: 4px; }

/* Cost comparison layout */
/* Cost table */
.cost-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 16px;
}
.cost-tbl th {
  font-size: 13px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--dim);
  font-weight: 400;
  padding: 0 8px 4px 0;
  text-align: right;
  white-space: nowrap;
}
.cost-tbl th:first-child { text-align: left; }
.cost-tbl td {
  padding: 2px 8px 2px 0;
  text-align: right;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.cost-tbl td:first-child {
  text-align: left;
  color: var(--dim);
  font-size: 15px;
}
.cost-tbl .cost-accent { font-weight: 700; font-size: 19px; }
.cost-tbl .row-savings td { border-top: 1px solid var(--border); padding-top: 4px; }
.spot-stale { font-size: 13px; color: var(--orange); margin-top: 4px; }

/* Instance info row */
.inst-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 15px;
}
.inst-row .inst-item { color: var(--dim); white-space: nowrap; }
.inst-row .inst-val { color: var(--text); font-weight: 600; }

/* GPU metrics */
.gpu-metric { margin: 10px 0; }
.gpu-metric-header { display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px; }
.gpu-metric-label { font-size: 13px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; }
.gpu-metric-value { font-size: 15px; font-weight: 700; color: var(--text); white-space: nowrap; }
.gpu-bar-track {
  height: 6px; width: 100%;
  background: var(--bg); border-radius: 3px; overflow: hidden;
}
.gpu-bar-fill {
  height: 100%; border-radius: 3px;
  transition: width 0.5s ease, background 0.5s ease;
  width: 0%;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 15px;
  font-weight: 600;
  margin-right: 4px;
  margin-bottom: 4px;
}
.badge-green { background: var(--green); color: #000; }
.badge-red { background: var(--red); color: #000; }

/* Log */
.log-box {
  background: var(--bg);
  border-radius: 6px;
  padding: 8px;
  max-height: 280px;
  overflow-y: auto;
  overflow-x: hidden;
  font-size: 13px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-all;
}
.log-box .eval-line { color: var(--yellow); }
.log-box .step-line { color: var(--text); }

/* Charts */
.chart-container { position: relative; height: 240px; }

/* Checkpoint list */
.ckpt-list { font-size: 15px; color: var(--dim); }
.ckpt-list span {
  display: inline-block;
  margin: 2px 3px;
  padding: 1px 5px;
  background: var(--bg);
  border-radius: 3px;
}

/* Bootstrap panel */
.bootstrap-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 14px;
  margin-bottom: 12px;
  transition: opacity 0.8s ease, max-height 0.8s ease;
}
.bootstrap-panel.hidden { display: none; }
.bootstrap-panel h2 { font-size: 15px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--dim); margin-bottom: 8px; }
.bs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.bs-header .bs-elapsed { font-size: 15px; color: var(--dim); }
.bs-progress-outer {
  width: 100%;
  height: 6px;
  background: var(--bg);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 10px;
}
.bs-progress-inner {
  height: 100%;
  border-radius: 3px;
  transition: width 0.5s ease, background 0.3s ease;
  background: var(--accent);
}
.bs-progress-inner.done { background: var(--green); }
.bs-progress-inner.failed { background: var(--red); }
.bs-steps {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(190px, 1fr));
  gap: 4px 12px;
}
.bs-step {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
}
.bs-step .bs-icon { width: 14px; text-align: center; flex-shrink: 0; }
.bs-step .bs-label { color: var(--dim); overflow: hidden; text-overflow: ellipsis; }
.bs-step .bs-time { color: var(--dim); font-size: 13px; margin-left: auto; flex-shrink: 0; }
.bs-step.done .bs-icon { color: var(--green); }
.bs-step.done .bs-label { color: var(--text); }
.bs-step.running .bs-icon { color: var(--accent); }
.bs-step.running .bs-label { color: var(--text); }
.bs-step.failed .bs-icon { color: var(--red); }
.bs-step.failed .bs-label { color: var(--red); }
.bs-step.pending .bs-icon { color: var(--dim); }
@keyframes spin { to { transform: rotate(360deg); } }
.bs-spinner { display: inline-block; animation: spin 1s linear infinite; }

/* Responsive */
@media (max-width: 900px) {
  .grid { grid-template-columns: 1fr; }
  .bs-steps { grid-template-columns: 1fr; }
}

/* Mobile header — hamburger menu */
.header-hamburger {
  display: none;
  background: none;
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text);
  font-size: 18px;
  line-height: 1;
}
.header-menu {
  display: none;
  position: absolute;
  top: 100%;
  right: 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  flex-direction: column;
  gap: 2px;
  padding: 8px;
  z-index: 100;
  box-shadow: 0 8px 24px rgba(0,0,0,0.4);
}
.header-menu.open { display: flex; }
.header-menu a {
  color: var(--text);
  text-decoration: none;
  padding: 8px 14px;
  border-radius: 6px;
  font-size: 14px;
  white-space: nowrap;
  transition: background 0.2s;
}
.header-menu a:hover { background: var(--bg); }

@media (max-width: 540px) {
  .header-links { display: none; }
  .header-hamburger { display: block; }
  .header h1 { font-size: 17px; }
  .header-sub { position: relative; }
  .modal-content { padding: 18px 16px; width: 95%; }
  .sitrep-body { font-size: 13px; }
}

/* Session breakdown table */
.session-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  margin-top: 8px;
}
.session-tbl th {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--dim);
  font-weight: 400;
  padding: 4px 6px 4px 0;
  text-align: left;
  white-space: nowrap;
}
.session-tbl td {
  padding: 3px 6px 3px 0;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
  color: var(--text);
}
.session-tbl td.dim { color: var(--dim); }

/* Footer */
.footer {
  margin-top: 16px;
  padding: 24px 14px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 17px;
  color: var(--dim);
}
.footer-links { display: flex; gap: 8px; font-size: 15px; }
.footer-links a {
  color: var(--text);
  text-decoration: none;
  padding: 5px 14px;
  border: 1px solid var(--border);
  border-radius: 14px;
  background: var(--bg);
  transition: border-color 0.2s, background 0.2s;
}
.footer-links a:hover {
  border-color: var(--accent);
  background: rgba(232, 121, 84, 0.1);
}
/* ── Sitrep modal ── */
.modal { position: fixed; inset: 0; background: rgba(0,0,0,0.6); display: flex;
  align-items: center; justify-content: center; z-index: 1000; }
.modal.hidden { display: none; }
.modal-content { background: var(--surface); border: 1px solid var(--border);
  border-radius: 12px; max-width: 910px; width: 90%; max-height: 80vh;
  overflow-y: auto; padding: 28px 32px; position: relative; }
.modal-close { position: absolute; top: 12px; right: 16px; background: none;
  border: none; color: var(--dim); font-size: 24px; cursor: pointer; line-height: 1; }
.modal-close:hover { color: var(--text); }
.modal-content { border-color: rgba(167, 139, 250, 0.2); }
.modal-content h2 { margin: 0 0 4px 0; font-size: 20px; color: #a78bfa; }
.sitrep-time { color: var(--dim); font-size: 12px; margin-bottom: 16px; }
.sitrep-body { font-size: 14px; line-height: 1.7; color: var(--text); }
.sitrep-body h1, .sitrep-body h2, .sitrep-body h3 {
  color: #a78bfa; margin: 18px 0 8px 0; font-size: 16px;
  border-bottom: 1px solid rgba(167, 139, 250, 0.15); padding-bottom: 6px; }
.sitrep-body h1 { font-size: 18px; }
.sitrep-body ul { margin: 4px 0 12px 0; padding-left: 20px; }
.sitrep-body li { margin-bottom: 3px; }
.sitrep-body li::marker { color: rgba(167, 139, 250, 0.5); }
.sitrep-body ol { margin: 4px 0 12px 0; padding-left: 20px; }
.sitrep-body code { background: rgba(167, 139, 250, 0.06); padding: 1px 5px; border-radius: 4px;
  font-size: 13px; border: 1px solid rgba(167, 139, 250, 0.15); color: #a78bfa; }
.sitrep-body p { margin: 0 0 10px 0; }
.sitrep-body strong { color: #a78bfa; }
.sitrep-body table { width: 100%; border-collapse: collapse; margin: 8px 0 12px; font-size: 13px; }
.sitrep-body th { text-align: left; color: #a78bfa; border-bottom: 1px solid rgba(167, 139, 250, 0.2); padding: 4px 8px; }
.sitrep-body td { padding: 4px 8px; border-bottom: 1px solid var(--border); }
.sitrep-body hr { border: none; border-top: 1px solid rgba(167,139,250,0.15); margin: 16px 0; }
.sitrep-body blockquote { border-left: 3px solid rgba(167,139,250,0.3); margin: 8px 0; padding: 4px 12px; color: var(--dim); }
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <h1><span class="pulse" id="pulse"></span>Dual-Process Language Model</h1>
    <div class="header-sub">
      <div class="header-links">
        <a href="https://bitbanshee.com" target="_blank">Bitbanshee</a>
        <a href="https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment" target="_blank">GitHub</a>
        <a href="/reports/v4/" target="_blank">Reports</a>
        <a href="#" class="sitrep-badge" onclick="openSitrep();return false">SITREP</a>
      </div>
      <button class="header-hamburger" onclick="document.getElementById('header-menu').classList.toggle('open')">&#9776;</button>
      <div class="header-menu" id="header-menu">
        <a href="https://bitbanshee.com" target="_blank">Bitbanshee</a>
        <a href="https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment" target="_blank">GitHub</a>
        <a href="/reports/v4/" target="_blank">Reports</a>
        <a href="#" class="sitrep-badge" onclick="document.getElementById('header-menu').classList.remove('open');openSitrep();return false">SITREP</a>
      </div>
      <div class="meta">
        <span id="conn-status">Connecting...</span> &middot;
        <span id="timestamp"></span>
      </div>
    </div>
  </div>

  <!-- Bootstrap progress -->
  <div id="bootstrap-panel" class="bootstrap-panel hidden">
    <div class="bs-header">
      <h2>Bootstrap Progress</h2>
      <span class="bs-elapsed" id="bs-elapsed"></span>
    </div>
    <div class="bs-progress-outer">
      <div class="bs-progress-inner" id="bs-progress" style="width:0%"></div>
    </div>
    <div class="bs-steps" id="bs-steps"></div>
  </div>

  <!-- Progress -->
  <div class="card card-full">
    <h2>Training Progress</h2>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px; margin-bottom:4px; font-size: 16px">
      <span>Step <strong id="cur-step">--</strong> / <span id="max-step">--</span></span>
      <span>Phase: <strong id="phase">--</strong></span>
      <span>Remaining: <strong id="eta">--</strong></span>
    </div>
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px; margin-bottom:6px">
      <div style="display:flex; gap:24px; font-size: 15px; color:var(--dim)">
        <span>Total Training Time: <strong style="color:var(--text)" id="total-time">--</strong></span>
        <span>This Instance: <strong style="color:var(--text)" id="elapsed">--</strong></span>
      </div>
      <div id="milestones" style="font-size: 14px; color:var(--dim)"></div>
    </div>
    <div class="progress-outer">
      <div class="progress-inner" id="progress-bar" style="width:0%">0%</div>
    </div>
  </div>

  <div class="grid">

    <!-- Live Metrics -->
    <div class="card">
      <h2>Live Metrics</h2>
      <div class="metrics-row">
        <div class="metric-box">
          <div class="label">AR Loss</div>
          <div class="value" id="m-ar-loss">--</div>
          <canvas id="spark-ar" width="100" height="28"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">Diff Loss</div>
          <div class="value" id="m-diff-loss">--</div>
          <canvas id="spark-diff" width="100" height="28"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">Conf Acc</div>
          <div class="value" id="m-conf-acc">--</div>
          <canvas id="spark-conf" width="100" height="28"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">AUROC</div>
          <div class="value" id="m-auroc">--</div>
          <canvas id="spark-auroc" width="100" height="28"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">S1 Acc</div>
          <div class="value" id="m-s1-acc">--</div>
          <canvas id="spark-s1" width="100" height="28"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">LR</div>
          <div class="value" id="m-lr">--</div>
          <canvas id="spark-lr" width="100" height="28"></canvas>
        </div>
      </div>
    </div>

    <!-- Instance, GPU & Cost -->
    <div class="card">
      <h2>Instance & GPU</h2>
      <div class="inst-row" style="margin-bottom:8px">
        <span class="inst-item"><span class="inst-val" id="inst-type">--</span></span>
        <span class="inst-item"><span class="inst-val" id="inst-lifecycle">--</span></span>
        <span class="inst-item"><span class="inst-val" id="inst-az">--</span></span>
        <span class="inst-item">up <span class="inst-val" id="inst-uptime">--</span></span>
      </div>
      <div id="gpu-name" style="color:var(--dim);font-size:14px;margin-bottom:6px">--</div>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px 16px;margin-bottom:10px">
        <div class="gpu-metric" style="margin:0">
          <div class="gpu-metric-header">
            <span class="gpu-metric-label">Utilization</span>
            <span class="gpu-metric-value" id="gpu-util-val">--</span>
          </div>
          <div class="gpu-bar-track"><div class="gpu-bar-fill" id="gpu-util-bar"></div></div>
        </div>
        <div class="gpu-metric" style="margin:0">
          <div class="gpu-metric-header">
            <span class="gpu-metric-label">VRAM</span>
            <span class="gpu-metric-value" id="gpu-vram-val">--</span>
          </div>
          <div class="gpu-bar-track"><div class="gpu-bar-fill" id="gpu-vram-bar"></div></div>
        </div>
        <div class="gpu-metric" style="margin:0">
          <div class="gpu-metric-header">
            <span class="gpu-metric-label">Temp</span>
            <span class="gpu-metric-value" id="gpu-temp-val">--</span>
          </div>
          <div class="gpu-bar-track"><div class="gpu-bar-fill" id="gpu-temp-bar"></div></div>
        </div>
        <div class="gpu-metric" style="margin:0">
          <div class="gpu-metric-header">
            <span class="gpu-metric-label">Power</span>
            <span class="gpu-metric-value" id="gpu-power-val">--</span>
          </div>
          <div class="gpu-bar-track"><div class="gpu-bar-fill" id="gpu-power-bar"></div></div>
        </div>
      </div>
      <div style="border-top:1px solid var(--border);padding-top:8px">
        <table class="cost-tbl">
          <tr><th></th><th>Rate</th><th>Cost</th><th>Projected</th></tr>
          <tr style="color:var(--red)">
            <td>On-Demand</td>
            <td id="od-rate">--</td>
            <td class="cost-accent" id="od-cost">--</td>
            <td id="od-proj">--</td>
          </tr>
          <tr style="color:var(--green)">
            <td>Spot</td>
            <td id="spot-rate">--</td>
            <td class="cost-accent" id="spot-cost">--</td>
            <td id="spot-proj">--</td>
          </tr>
          <tr class="row-savings">
            <td>Savings</td>
            <td id="delta-pct">--</td>
            <td class="cost-accent" id="delta-cost">--</td>
            <td id="delta-proj">--</td>
          </tr>
        </table>
        <div class="spot-stale" id="spot-stale" style="display:none"></div>
      </div>
    </div>

    <!-- Loss chart -->
    <div class="card">
      <h2>Loss Curves</h2>
      <div class="chart-container"><canvas id="chart-loss"></canvas></div>
    </div>

    <!-- Eval chart -->
    <div class="card">
      <h2>Eval Metrics <span id="eval-chart-note" style="font-weight:400;text-transform:none;letter-spacing:0;color:var(--dim)"></span></h2>
      <div class="chart-container"><canvas id="chart-eval"></canvas></div>
    </div>

    <!-- Infra -->
    <div class="card">
      <h2>Infrastructure</h2>
      <div style="margin-bottom:6px">
        <span class="badge" id="badge-trainer">Trainer: ?</span>
        <span class="badge" id="badge-sync">Sync: ?</span>
      </div>
      <div style="margin-bottom:6px">
        <span style="font-size: 13px;color:var(--dim);text-transform:uppercase;letter-spacing:0.06em">Config</span>
        <div id="config-info" style="font-size: 14px;color:var(--dim);margin-top:2px">--</div>
      </div>
      <div>
        <span style="font-size: 13px;color:var(--dim);text-transform:uppercase;letter-spacing:0.06em">Checkpoints: v4</span>
        <div id="last-ckpt" style="font-size: 14px; margin: 3px 0 4px; color:var(--green)"></div>
        <div class="ckpt-list" id="ckpt-list">--</div>
      </div>
      <div id="sessions-breakdown" style="display:none;margin-top:8px;padding:8px 0 0;border-top:1px solid var(--border)">
        <span style="font-size: 13px;color:var(--dim);text-transform:uppercase;letter-spacing:0.06em">Instance History</span>
        <table class="session-tbl" id="sessions-table">
          <tr><th>#</th><th>AZ</th><th>Steps</th><th>Duration</th><th>Cost</th></tr>
        </table>

      </div>
      <div id="cost-controls" style="margin-top:8px;padding:8px 0 0;border-top:1px solid var(--border);font-size:13px;display:none"></div>
    </div>

    <!-- Log tail -->
    <div class="card" style="display:flex;flex-direction:column">
      <h2>Log Tail</h2>
      <div class="log-box" id="log-tail" style="flex:1;max-height:none">--</div>
    </div>

  </div>

  <!-- Footer -->
  <div class="footer">
    <span>Dual-Process Language Model</span>
    <div class="footer-links">
      <a href="https://bitbanshee.com" target="_blank">bitbanshee.com</a>
      <a href="/reports/v4/" target="_blank">Reports</a>
    </div>
  </div>
</div>

<script>
// ── Chart setup ──────────────────────────────────────────────────────────
const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 300 },
  plugins: { legend: { labels: { color: '#888', font: { size: 10, family: 'monospace' } } } },
  scales: {
    x: { ticks: { color: '#555', font: { size: 9 } }, grid: { color: '#1f2233' } },
    y: { ticks: { color: '#555', font: { size: 9 } }, grid: { color: '#1f2233' } },
  },
};

const lossChart = new Chart(document.getElementById('chart-loss'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'AR Loss', data: [], borderColor: '#60a5fa', borderWidth: 1.5, pointRadius: 0, tension: 0.3 },
      { label: 'Diff Loss', data: [], borderColor: '#fb923c', borderWidth: 1.5, pointRadius: 0, tension: 0.3 },
    ],
  },
  options: { ...chartOpts },
});

const evalChart = new Chart(document.getElementById('chart-eval'), {
  type: 'line',
  data: {
    labels: [],
    datasets: [
      { label: 'S1 Tok Acc', data: [], borderColor: '#34d399', borderWidth: 2, pointRadius: 3, tension: 0.3, yAxisID: 'y' },
      { label: 'AUROC', data: [], borderColor: '#a78bfa', borderWidth: 2, pointRadius: 3, tension: 0.3, yAxisID: 'y' },
      { label: 'AR PPL', data: [], borderColor: '#f87171', borderWidth: 2, pointRadius: 3, tension: 0.3, yAxisID: 'y1' },
    ],
  },
  options: {
    ...chartOpts,
    scales: {
      ...chartOpts.scales,
      y: { ...chartOpts.scales.y, position: 'left', title: { display: true, text: 'Acc / AUROC', color: '#555' } },
      y1: { ...chartOpts.scales.y, position: 'right', title: { display: true, text: 'PPL', color: '#555' }, grid: { drawOnChartArea: false } },
    },
  },
});

// ── Sparklines ───────────────────────────────────────────────────────────
const sparkBuffers = { ar: [], diff: [], conf: [], auroc: [], s1: [], lr: [] };
const SPARK_MAX = 30;

function drawSparkline(canvasId, data, color) {
  const canvas = document.getElementById(canvasId);
  if (!canvas || data.length < 2) return;
  const ctx = canvas.getContext('2d');
  const w = canvas.width, h = canvas.height;
  ctx.clearRect(0, 0, w, h);
  const min = Math.min(...data), max = Math.max(...data);
  const range = max - min || 1;
  ctx.beginPath();
  ctx.strokeStyle = color;
  ctx.lineWidth = 1.5;
  data.forEach((v, i) => {
    const x = (i / (data.length - 1)) * w;
    const y = h - ((v - min) / range) * (h - 4) - 2;
    i === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y);
  });
  ctx.stroke();
}

// ── Chart refresh ────────────────────────────────────────────────────────
let currentTrainStep = 0;
let lastEvalStep = null;
let lastTrainStep = null;
let lastChartRefresh = Date.now();

function checkChartRefresh(data) {
  let needsRefresh = false;

  // Refresh when new training steps appear
  const trainStep = data.current_step || 0;
  if (trainStep > 0 && trainStep !== lastTrainStep) {
    lastTrainStep = trainStep;
    needsRefresh = true;
  }

  // Refresh when new eval data appears
  const evalStep = data.latest_eval ? data.latest_eval.step : null;
  if (evalStep !== null && evalStep !== lastEvalStep) {
    lastEvalStep = evalStep;
    needsRefresh = true;
  }

  if (needsRefresh) {
    lastChartRefresh = Date.now();
    loadCharts();
  }
}

// ── Bootstrap panel ──────────────────────────────────────────────────────
function updateBootstrap(bs) {
  const panel = $('bootstrap-panel');

  // Hide if no data, or if all steps are done
  if (!bs || bs.status === 'done') {
    panel.classList.add('hidden');
    return;
  }

  // Has incomplete/failed steps — show the panel
  panel.classList.remove('hidden');

  const steps = bs.steps || [];
  const doneCount = steps.filter(s => s.status === 'done').length;
  const total = steps.length || 1;
  const pct = (doneCount / total * 100).toFixed(0);

  // Progress bar
  const bar = $('bs-progress');
  bar.style.width = pct + '%';
  bar.className = 'bs-progress-inner' + (bs.status === 'failed' ? ' failed' : '');

  // Elapsed
  const elapsedEl = $('bs-elapsed');
  if (bs.total_elapsed_s != null) {
    elapsedEl.textContent = fmtTimeLong(bs.total_elapsed_s);
  } else {
    elapsedEl.textContent = '';
  }

  // Steps
  const container = $('bs-steps');
  container.innerHTML = steps.map(s => {
    let icon;
    if (s.status === 'done') icon = '\u2713';
    else if (s.status === 'running') icon = '<span class="bs-spinner">\u25E0</span>';
    else if (s.status === 'failed') icon = '\u2717';
    else icon = '\u2022';
    const elapsed = s.elapsed != null ? s.elapsed.toFixed(1) + 's' : '';
    return '<div class="bs-step ' + s.status + '">' +
      '<span class="bs-icon">' + icon + '</span>' +
      '<span class="bs-label">' + esc(s.label) + '</span>' +
      '<span class="bs-time">' + elapsed + '</span>' +
      '</div>';
  }).join('');
}

// ── Cost ticker ──────────────────────────────────────────────────────────
let costState = { bootTime: null, odRate: null, spotRate: null, spotCostBase: null, spotCostBaseTime: null };

function tickCost() {
  if (!costState.bootTime) return;
  const now = Date.now() / 1000;
  const uptime = now - costState.bootTime;
  document.getElementById('inst-uptime').textContent = fmtTimeLong(uptime);
  // On-demand ticker
  if (costState.odRate) {
    const odCost = costState.odRate * uptime / 3600;
    document.getElementById('od-cost').textContent = '$' + odCost.toFixed(2);
  }
  // Spot ticker: extrapolate from last known base using current rate
  if (costState.spotRate && costState.spotCostBase != null && costState.spotCostBaseTime) {
    const dt = now - costState.spotCostBaseTime;
    const spotCost = costState.spotCostBase + costState.spotRate * dt / 3600;
    document.getElementById('spot-cost').textContent = '$' + spotCost.toFixed(2);
    // Update savings in real time
    if (costState.odRate) {
      const odCost = costState.odRate * uptime / 3600;
      const saved = odCost - spotCost;
      document.getElementById('delta-cost').textContent = '$' + saved.toFixed(2);
      const pct = odCost > 0 ? ((1 - spotCost / odCost) * 100).toFixed(1) : 0;
      document.getElementById('delta-pct').textContent = pct + '% less';
    }
  }
}
setInterval(tickCost, 1000);

// ── Format helpers ───────────────────────────────────────────────────────
function fmtTimeLong(s) {
  if (s == null) return '--';
  s = Math.round(s);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  const sec = s % 60;
  if (h > 0) return h + 'h ' + m + 'm ' + sec + 's';
  if (m > 0) return m + 'm ' + sec + 's';
  return sec + 's';
}

function fmtTime(s) {
  if (s == null) return '--';
  s = Math.round(s);
  const h = Math.floor(s / 3600);
  const m = Math.floor((s % 3600) / 60);
  if (h > 0) return h + 'h ' + m + 'm';
  return m + 'm';
}



function $(id) { return document.getElementById(id); }

// ── RAG (red/amber/green) metric coloring ────────────────────────────────
// Thresholds tuned to GPT-2 small training trajectory.
// "lower" = lower is better; "higher" = higher is better.
function setRAG(elementId, value, thresholds) {
  const el = $(elementId);
  if (!el) return;
  const box = el.closest('.metric-box');
  if (!box) return;
  box.classList.remove('rag-green', 'rag-amber', 'rag-red');
  if (value == null) return;
  let cls;
  if (thresholds.dir === 'lower') {
    cls = value < thresholds.green ? 'rag-green' : value < thresholds.red ? 'rag-amber' : 'rag-red';
  } else {
    cls = value > thresholds.green ? 'rag-green' : value > thresholds.red ? 'rag-amber' : 'rag-red';
  }
  box.classList.add(cls);
}
const RAG = {
  ar_loss:   { dir: 'lower',  green: 3.0, red: 5.0 },
  diff_loss: { dir: 'lower',  green: 5.0, red: 7.0 },
  conf_acc:  { dir: 'higher', green: 0.90, red: 0.75 },
  auroc:     { dir: 'higher', green: 0.75, red: 0.58 },
  s1_acc:   { dir: 'higher', green: 0.10, red: 0.05 },
};

// ── UI updater ───────────────────────────────────────────────────────────
function updateUI(data) {
  const _ts = new Date(data.timestamp);
  const _et = _ts.toLocaleTimeString('en-US', {timeZone:'America/New_York', hour:'numeric', minute:'2-digit'});
  const _utc = _ts.toLocaleTimeString('en-US', {timeZone:'UTC', hour:'2-digit', minute:'2-digit', hour12:false});
  $('timestamp').textContent = _et + ' ET / ' + _utc + ' UTC';

  // Track current training step for chart filtering
  currentTrainStep = data.current_step || 0;

  // Bootstrap
  if (data.bootstrap) updateBootstrap(data.bootstrap);

  // Refresh charts when new eval data appears or every 5 min
  checkChartRefresh(data);

  // Progress
  $('cur-step').textContent = data.current_step.toLocaleString();
  $('max-step').textContent = data.max_steps.toLocaleString();
  $('phase').textContent = data.phase;
  $('total-time').textContent = data.total_training_time_s ? fmtTime(data.total_training_time_s) : fmtTime(data.elapsed_seconds);
  $('elapsed').textContent = fmtTime(data.elapsed_seconds);
  $('eta').textContent = fmtTime(data.eta_seconds);
  const pct = data.progress_pct;
  const bar = $('progress-bar');
  bar.style.width = pct + '%';
  bar.textContent = pct.toFixed(1) + '%';

  // Instance & cost
  const inst = data.instance;
  if (inst) {
    $('inst-type').textContent = inst.instance_type || '--';
    $('inst-lifecycle').textContent = inst.lifecycle || '--';
    $('inst-az').textContent = inst.az || '--';
    if (inst.uptime_seconds != null) $('inst-uptime').textContent = fmtTimeLong(inst.uptime_seconds);

    if (inst.boot_time_utc) costState.bootTime = new Date(inst.boot_time_utc).getTime() / 1000;

    // On-demand
    const odRate = inst.ondemand_price_per_hour;
    if (odRate) {
      costState.odRate = odRate;
      $('od-rate').textContent = '$' + odRate.toFixed(4) + '/hr';
    }
    if (inst.ondemand_cost != null) $('od-cost').textContent = '$' + inst.ondemand_cost.toFixed(2);
    $('od-proj').textContent = inst.ondemand_projected != null ? '$' + inst.ondemand_projected.toFixed(2) : '--';

    // Spot
    if (inst.spot_rate != null) {
      costState.spotRate = inst.spot_rate;
      $('spot-rate').textContent = '$' + inst.spot_rate.toFixed(4) + '/hr';
    } else {
      $('spot-rate').textContent = '--';
    }
    if (inst.spot_cost != null) {
      $('spot-cost').textContent = '$' + inst.spot_cost.toFixed(2);
      costState.spotCostBase = inst.spot_cost;
      costState.spotCostBaseTime = Date.now() / 1000;
    } else {
      $('spot-cost').textContent = '--';
    }
    $('spot-proj').textContent = inst.spot_projected != null ? '$' + inst.spot_projected.toFixed(2) : '--';

    // Staleness
    const staleEl = $('spot-stale');
    if (inst.spot_updated) {
      const age = (Date.now() - new Date(inst.spot_updated).getTime()) / 60000;
      if (age > 30) {
        staleEl.style.display = 'block';
        staleEl.textContent = 'Spot price data ' + Math.round(age) + 'min old';
      } else {
        staleEl.style.display = 'none';
      }
    } else if (inst.spot_rate == null) {
      staleEl.style.display = 'block';
      staleEl.textContent = 'Spot price data loading\u2026';
    }

    // Savings row
    if (inst.savings != null) {
      $('delta-cost').textContent = '$' + inst.savings.toFixed(2);
      $('delta-pct').textContent = inst.savings_pct.toFixed(1) + '%';
    }
    if (inst.ondemand_projected != null && inst.spot_projected != null) {
      $('delta-proj').textContent = '$' + (inst.ondemand_projected - inst.spot_projected).toFixed(2);
    }

    // Run total cost (across all spot sessions)
    if (inst.total_run_cost != null) {
    }

    // Cost controls display
    if (data.cost_controls && data.cost_controls.max_budget > 0) {
      const cc = data.cost_controls;
      const totalCost = inst.total_run_cost || 0;
      const budgetPct = (totalCost / cc.max_budget * 100);
      const budgetColor = budgetPct > 90 ? 'var(--red)' : budgetPct > 70 ? 'var(--yellow)' : 'var(--green)';
      const spotRate = inst.spot_rate || 0;
      const spotPct = cc.max_spot_price > 0 ? (spotRate / cc.max_spot_price * 100) : 0;
      const spotColor = spotPct > 80 ? 'var(--red)' : spotPct > 50 ? 'var(--yellow)' : 'var(--green)';

      const ccEl = document.getElementById('cost-controls');
      if (ccEl) {
        ccEl.style.display = 'block';
        ccEl.innerHTML =
          '<span style="color:' + budgetColor + '">Budget: $' + totalCost.toFixed(2) + ' / $' + cc.max_budget.toFixed(0) + '</span>' +
          ' &middot; ' +
          '<span style="color:' + spotColor + '">Ceiling: $' + cc.max_spot_price.toFixed(2) + '/hr</span>' +
          ' &middot; ' +
          '<span>Rate: $' + spotRate.toFixed(4) + '/hr</span>';
      }
    }
  }

  // Session breakdown (instance history)
  const sessions = data.sessions_breakdown;
  if (sessions && sessions.length > 1) {
    $('sessions-breakdown').style.display = 'block';
    const tbl = $('sessions-table');
    tbl.innerHTML = '<tr><th>#</th><th>AZ</th><th>Steps</th><th>Duration</th><th>Cost</th></tr>';
    sessions.forEach((s, i) => {
      const az = s.az ? s.az.replace('us-east-1', '1') : '?';
      const steps = (s.steps_start != null && s.steps_end != null)
        ? (s.steps_start/1000).toFixed(1) + 'k\u2192' + (s.steps_end/1000).toFixed(1) + 'k'
        : '--';
      const dur = s.duration_s != null ? fmtTime(s.duration_s) : '--';
      const cost = s.spot_cost != null ? '$' + s.spot_cost.toFixed(2) : '--';
      const cls = s.finalized ? '' : ' style="color:var(--accent)"';
      tbl.innerHTML += '<tr' + cls + '><td class="dim">' + (i+1) + '</td><td>' + esc(az) + '</td><td>' + steps + '</td><td>' + dur + '</td><td>' + cost + '</td></tr>';
    });
    // Run total as footer row aligned to Cost column
    if (inst && inst.total_run_cost != null) {
      const sessLabel = inst.total_sessions > 1 ? '(' + inst.total_sessions + ' sessions)' : '(1 session)';
      tbl.innerHTML += '<tr style="border-top:1px solid var(--border)"><td colspan="4" style="padding-top:5px;color:var(--dim);font-size:13px">Run Total ' + sessLabel + '</td><td style="padding-top:5px;font-weight:600;color:var(--accent)">$' + inst.total_run_cost.toFixed(2) + '</td></tr>';
    }
  }

  // Live metrics
  const t = data.latest_train;
  if (t) {
    $('m-ar-loss').textContent = t.ar_loss.toFixed(4);
    $('m-diff-loss').textContent = t.diff_loss.toFixed(4);
    $('m-lr').textContent = t.lr.toExponential(2);

    setRAG('m-ar-loss', t.ar_loss, RAG.ar_loss);
    setRAG('m-diff-loss', t.diff_loss, RAG.diff_loss);
    setRAG('m-conf-acc', t.conf_acc, RAG.conf_acc);

    sparkBuffers.ar.push(t.ar_loss);
    sparkBuffers.diff.push(t.diff_loss);
    sparkBuffers.lr.push(t.lr);
    for (const k of ['ar', 'diff', 'lr']) {
      if (sparkBuffers[k].length > SPARK_MAX) sparkBuffers[k].shift();
    }
    drawSparkline('spark-ar', sparkBuffers.ar, '#60a5fa');
    drawSparkline('spark-diff', sparkBuffers.diff, '#fb923c');
    drawSparkline('spark-lr', sparkBuffers.lr, '#a78bfa');
  }

  // Eval-sourced metrics (only from current run)
  const ev = data.latest_eval;
  const awaitMsg = data.next_eval_step ? 'eval @ ' + data.next_eval_step.toLocaleString() : '--';
  if (ev) {
    $('m-conf-acc').style.fontSize = '';
    $('m-conf-acc').textContent = ((ev.conf_accuracy ?? ev.conf_acc ?? 0) * 100).toFixed(1) + '%';
    setRAG('m-conf-acc', ev.conf_accuracy ?? ev.conf_acc ?? 0, RAG.conf_acc);

    if (ev.conf_auroc != null) {
      $('m-auroc').style.fontSize = '';
      $('m-auroc').textContent = ev.conf_auroc.toFixed(4);
      setRAG('m-auroc', ev.conf_auroc, RAG.auroc);
    }

    const s1val = ev.s1_tok_acc ?? ev.s1_token_accuracy ?? null;
    if (s1val != null) {
      $('m-s1-acc').style.fontSize = '';
      $('m-s1-acc').textContent = (s1val * 100).toFixed(1) + '%';
      setRAG('m-s1-acc', s1val, RAG.s1_acc);
    }

    // Only push to eval sparklines when a new eval step arrives
    const evalStep = ev.step ?? null;
    if (evalStep && evalStep !== lastEvalStep) {
      lastEvalStep = evalStep;
      sparkBuffers.conf.push(ev.conf_accuracy ?? ev.conf_acc ?? 0);
      if (sparkBuffers.conf.length > SPARK_MAX) sparkBuffers.conf.shift();
      if (ev.conf_auroc != null) {
        sparkBuffers.auroc.push(ev.conf_auroc);
        if (sparkBuffers.auroc.length > SPARK_MAX) sparkBuffers.auroc.shift();
      }
      if (s1val != null) {
        sparkBuffers.s1.push(s1val);
        if (sparkBuffers.s1.length > SPARK_MAX) sparkBuffers.s1.shift();
      }
      drawSparkline('spark-conf', sparkBuffers.conf, '#34d399');
      drawSparkline('spark-auroc', sparkBuffers.auroc, '#a78bfa');
      drawSparkline('spark-s1', sparkBuffers.s1, '#34d399');
    }
  } else {
    $('m-conf-acc').textContent = awaitMsg;
    $('m-conf-acc').style.fontSize = '11px';
    $('m-auroc').textContent = awaitMsg;
    $('m-auroc').style.fontSize = '11px';
    $('m-s1-acc').textContent = awaitMsg;
    $('m-s1-acc').style.fontSize = '11px';
  }

  // Clear eval chart note
  const evalNote = $('eval-chart-note');
  if (evalNote) evalNote.textContent = '';

  // GPU
  const g = data.gpu;
  if (g) {
    $('gpu-name').textContent = g.name;
    setGpuMetric('gpu-util', g.gpu_util,
      g.gpu_util.toFixed(0) + '%');
    setGpuMetric('gpu-vram', g.vram_used_mb / g.vram_total_mb * 100,
      (g.vram_used_mb/1024).toFixed(1) + ' / ' + (g.vram_total_mb/1024).toFixed(1) + ' GB');
    setGpuMetric('gpu-temp', g.temp_c,
      g.temp_c.toFixed(0) + '°C', tempColor);
    setGpuMetric('gpu-power', g.power_w / g.power_limit_w * 100,
      g.power_w.toFixed(0) + ' / ' + g.power_limit_w.toFixed(0) + ' W');
  }

  // Infra
  const inf = data.infra;
  if (inf) {
    setBadge('badge-trainer', 'Trainer', inf.trainer_running);
    setBadge('badge-sync', 'Sync', inf.sync_running);
    const ckptEl = $('ckpt-list');
    const lastCkptEl = $('last-ckpt');
    if (inf.last_checkpoint) {
      lastCkptEl.innerHTML = '✓ <strong>' + esc(inf.last_checkpoint.name) + '</strong>' +
        ' <span style="color:var(--dim);font-size:13px">' + esc(inf.last_checkpoint.time_utc) +
        ' · ' + inf.last_checkpoint.size_mb + ' MB</span>';
    } else {
      lastCkptEl.textContent = '';
    }
    if (inf.checkpoints && inf.checkpoints.length > 0) {
      ckptEl.innerHTML = inf.checkpoints.map(c => '<span>' + esc(c) + '</span>').join(' ');
    } else {
      ckptEl.textContent = 'None yet';
    }
  }

  // Milestones
  const msEl = $('milestones');
  if (data.milestones && data.milestones.length > 0) {
    msEl.innerHTML = data.milestones.map(m => {
      const delta = m.step - data.current_step;
      return '<span style="margin-right:12px"><span style="color:var(--accent)">' +
        esc(m.label) + '</span> step ' + m.step.toLocaleString() +
        ' <span style="color:var(--dim)">(in ' + delta.toLocaleString() + ')</span></span>';
    }).join('');
  } else {
    msEl.textContent = '--';
  }

  // Config
  const cfg = data.config_summary;
  if (cfg) {
    $('config-info').textContent =
      cfg.model + ' | bs=' + cfg.batch_size + '\u00d7' + cfg.grad_accum +
      ' | lr=' + cfg.lr + ' | warmup=' + cfg.warmup_steps +
      ' | eval@' + cfg.eval_every + ' | ckpt@' + cfg.checkpoint_every;
  }

  // Log tail
  const logEl = $('log-tail');
  if (data.log_tail && data.log_tail.length > 0) {
    logEl.innerHTML = data.log_tail.map(line => {
      if (line.startsWith('[eval]')) return '<span class="eval-line">' + esc(line) + '</span>';
      return '<span class="step-line">' + esc(line) + '</span>';
    }).join('\n');
    logEl.scrollTop = logEl.scrollHeight;
  }
}

function setGpuMetric(prefix, pct, label, colorFn) {
  pct = Math.min(100, Math.max(0, pct));
  const bar = $(prefix + '-bar');
  const val = $(prefix + '-val');
  bar.style.width = pct + '%';
  bar.style.background = colorFn ? colorFn(pct) : gpuColor(pct);
  val.textContent = label;
}

// Util/VRAM: green=normal, yellow=high, red=critical
function gpuColor(pct) {
  if (pct > 95) return '#f87171';
  if (pct > 80) return '#fbbf24';
  return '#34d399';
}

// Temp: green<60, yellow 60-80, red>80 (mapped to 0-100 scale for the bar)
function tempColor(pct) {
  if (pct > 80) return '#f87171';
  if (pct > 60) return '#fbbf24';
  return '#34d399';
}

function setBadge(id, name, running) {
  const el = $(id);
  el.textContent = name + ': ' + (running ? 'Running' : 'Stopped');
  el.className = 'badge ' + (running ? 'badge-green' : 'badge-red');
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s;
  return d.innerHTML;
}

// ── Fetch charts on load ─────────────────────────────────────────────────
async function loadCharts() {
  try {
    const [histRes, evalRes] = await Promise.all([
      fetch('/api/history'),
      fetch('/api/eval/history'),
    ]);
    const hist = await histRes.json();
    const evals = await evalRes.json();

    lossChart.data.labels = hist.map(h => h.step);
    lossChart.data.datasets[0].data = hist.map(h => h.ar_loss);
    lossChart.data.datasets[1].data = hist.map(h => h.diff_loss);
    lossChart.update();

    const tail = hist.slice(-SPARK_MAX);
    sparkBuffers.ar = tail.map(h => h.ar_loss);
    sparkBuffers.diff = tail.map(h => h.diff_loss);
    sparkBuffers.lr = tail.map(h => h.lr);

    // Filter to current run: only show evals up to current training step
    const maxStep = currentTrainStep || Infinity;
    const filtered = evals.filter(e => e.step <= maxStep);
    if (filtered.length > 0) {
      evalChart.data.labels = filtered.map(e => e.step);
      evalChart.data.datasets[0].data = filtered.map(e => e.s1_tok_acc ?? e.s1_token_accuracy ?? null);
      evalChart.data.datasets[1].data = filtered.map(e => e.conf_auroc ?? null);
      evalChart.data.datasets[2].data = filtered.map(e => e.ar_ppl ?? e.ar_perplexity ?? null);
      evalChart.update();

      // Seed eval sparklines from history
      const evalTail = filtered.slice(-SPARK_MAX);
      sparkBuffers.conf = evalTail.map(e => e.conf_accuracy ?? e.conf_acc ?? 0);
      sparkBuffers.auroc = evalTail.map(e => e.conf_auroc ?? 0);
      sparkBuffers.s1 = evalTail.map(e => e.s1_tok_acc ?? e.s1_token_accuracy ?? 0);
      drawSparkline('spark-conf', sparkBuffers.conf, '#34d399');
      drawSparkline('spark-auroc', sparkBuffers.auroc, '#a78bfa');
      drawSparkline('spark-s1', sparkBuffers.s1, '#34d399');
      if (filtered.length > 0) lastEvalStep = filtered[filtered.length - 1].step;
    }
  } catch (e) {
    console.error('Failed to load charts:', e);
  }
}

// ── SSE ──────────────────────────────────────────────────────────────────
let evtSource;
function connectSSE() {
  evtSource = new EventSource('/stream');
  evtSource.onmessage = (e) => {
    $('conn-status').textContent = 'Live';
    $('pulse').style.background = '#34d399';
    try { const d = JSON.parse(e.data); updateUI(d); checkTermination(d); } catch (err) { console.error('SSE parse error:', err); }
  };
  evtSource.onerror = () => {
    $('conn-status').textContent = 'Reconnecting...';
    $('pulse').style.background = '#f87171';
    evtSource.close();
    setTimeout(connectSSE, 5000);
  };
}

// ── Sitrep modal ─────────────────────────────────────────────────────────
function renderMarkdown(md) {
  let html = '';
  const lines = md.split('\n');
  let inUl = false, inOl = false, inTable = false, isFirstTableRow = false, inBlockquote = false;
  for (let line of lines) {
    // Close lists if line doesn't continue them
    if (inUl && !/^\s*[-*]\s/.test(line)) { html += '</ul>'; inUl = false; }
    if (inOl && !/^\s*\d+\.\s/.test(line)) { html += '</ol>'; inOl = false; }
    // Close table if line is not a pipe row
    if (inTable && !/^\|/.test(line.trim())) { html += '</tbody></table>'; inTable = false; }
    // Close blockquote if line doesn't start with >
    if (inBlockquote && !/^>\s?/.test(line)) { html += '</blockquote>'; inBlockquote = false; }

    if (/^###\s+(.*)/.test(line)) {
      html += '<h3>' + RegExp.$1 + '</h3>';
    } else if (/^##\s+(.*)/.test(line)) {
      html += '<h2>' + RegExp.$1 + '</h2>';
    } else if (/^#\s+(.*)/.test(line)) {
      html += '<h1>' + RegExp.$1 + '</h1>';
    } else if (/^(---+|\*\*\*+|___+)\s*$/.test(line.trim())) {
      html += '<hr>';
    } else if (/^>\s?(.*)/.test(line)) {
      if (!inBlockquote) { html += '<blockquote>'; inBlockquote = true; }
      html += '<p>' + inlineFormat(RegExp.$1) + '</p>';
    } else if (/^\|.*\|/.test(line.trim())) {
      // Table row — skip separator rows like |---|---|
      if (/^\|[\s\-:|]+\|$/.test(line.trim())) continue;
      const cells = line.trim().replace(/^\||\|$/g, '').split('|').map(c => c.trim());
      if (!inTable) {
        // First data row → header
        html += '<table><thead><tr>' + cells.map(c => '<th>' + inlineFormat(c) + '</th>').join('') + '</tr></thead><tbody>';
        inTable = true;
      } else {
        html += '<tr>' + cells.map(c => '<td>' + inlineFormat(c) + '</td>').join('') + '</tr>';
      }
    } else if (/^\s*[-*]\s+(.*)/.test(line)) {
      if (!inUl) { html += '<ul>'; inUl = true; }
      html += '<li>' + inlineFormat(RegExp.$1) + '</li>';
    } else if (/^\s*(\d+)\.\s+(.*)/.test(line)) {
      if (!inOl) { html += '<ol>'; inOl = true; }
      html += '<li>' + inlineFormat(RegExp.$2) + '</li>';
    } else if (line.trim() === '') {
      html += '<br>';
    } else {
      html += '<p>' + inlineFormat(line) + '</p>';
    }
  }
  if (inUl) html += '</ul>';
  if (inOl) html += '</ol>';
  if (inTable) html += '</tbody></table>';
  if (inBlockquote) html += '</blockquote>';
  return html;
}

function inlineFormat(s) {
  s = s.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  s = s.replace(/`([^`]+)`/g, '<code>$1</code>');
  s = s.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>');
  return s;
}

async function openSitrep() {
  const modal = document.getElementById('sitrep-modal');
  const body = document.getElementById('sitrep-body');
  const timeEl = document.getElementById('sitrep-time');
  body.innerHTML = '<p style="color:var(--dim)">Loading...</p>';
  timeEl.textContent = '';
  modal.classList.remove('hidden');
  try {
    const res = await fetch('/api/sitrep');
    const data = await res.json();
    body.innerHTML = renderMarkdown(data.content);
    if (data.modified) {
      const d = new Date(data.modified);
      timeEl.textContent = 'Last updated: ' + d.toLocaleString();
    }
  } catch (e) {
    body.innerHTML = '<p style="color:#e74c3c">Failed to load sitrep.</p>';
  }
}

function closeSitrep() {
  document.getElementById('sitrep-modal').classList.add('hidden');
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') { closeSitrep(); closeTermNotice(); }
});

// ── Spot termination notice ──────────────────────────────────────────────
let _termDismissed = false;
function checkTermination(data) {
  if (!data.spot_termination || _termDismissed) return;
  const modal = $('term-modal');
  // Compute countdown to termination (updates every SSE tick)
  const termTime = new Date(data.spot_termination);
  const secsLeft = Math.max(0, Math.round((termTime - Date.now()) / 1000));
  const m = Math.floor(secsLeft / 60);
  const s = secsLeft % 60;
  $('term-countdown').textContent = m + ':' + (s < 10 ? '0' : '') + s;
  $('term-time').textContent = termTime.toLocaleTimeString();
  if (modal.classList.contains('hidden')) {
    // Update status badge on first show
    $('conn-status').textContent = 'Terminating';
    $('pulse').style.background = '#f87171';
    modal.classList.remove('hidden');
  }
}

function closeTermNotice() {
  $('term-modal').classList.add('hidden');
  _termDismissed = true;
}

// ── Init ─────────────────────────────────────────────────────────────────
async function init() {
  try {
    const res = await fetch('/api/status');
    updateUI(await res.json());
  } catch (e) {
    console.error('Initial status load failed:', e);
  }
  await loadCharts();
  connectSSE();
}

// -- SITREP badge freshness --
function updateSitrepBadge() {
  fetch('/api/sitrep').then(r => r.json()).then(data => {
    if (!data.modified) return;
    const age = (Date.now() - new Date(data.modified).getTime()) / 60000;
    const badges = document.querySelectorAll('.sitrep-badge, .sitrep-badge-fresh');
    badges.forEach(b => {
      if (age < 10) {
        b.className = b.className.replace('sitrep-badge', 'sitrep-badge-fresh');
        if (!b.className.includes('sitrep-badge-fresh')) b.className += ' sitrep-badge-fresh';
      } else {
        b.className = b.className.replace('sitrep-badge-fresh', 'sitrep-badge');
      }
    });
  }).catch(() => {});
}
setInterval(updateSitrepBadge, 30000);
setTimeout(updateSitrepBadge, 2000);

init();
</script>

<!-- Sitrep modal -->
<div id="sitrep-modal" class="modal hidden" onclick="if(event.target===this)closeSitrep()">
  <div class="modal-content">
    <button class="modal-close" onclick="closeSitrep()">&times;</button>
    <h2>SITREP</h2>
    <div id="sitrep-time" class="sitrep-time"></div>
    <div id="sitrep-body" class="sitrep-body"></div>
  </div>
</div>

<!-- Spot termination modal -->
<div id="term-modal" class="modal hidden" onclick="if(event.target===this)closeTermNotice()">
  <div class="modal-content" style="border-color:rgba(248,113,113,.3); max-width:480px; text-align:center;">
    <button class="modal-close" onclick="closeTermNotice()">&times;</button>
    <h2 style="color:#f87171; font-size:18px;">Spot Instance Terminating</h2>
    <p style="font-size:40px; font-weight:700; color:#f87171; margin:16px 0 8px;" id="term-countdown">--:--</p>
    <p style="color:var(--dim); font-size:14px; margin-bottom:14px;">
      AWS is reclaiming this spot instance at <strong id="term-time">--</strong>
    </p>
    <p style="color:var(--text); font-size:14px; line-height:1.6; margin-bottom:12px;">
      A final sync of checkpoints, eval metrics, and logs to S3 is in progress.
      Training will resume automatically on the next spot instance launch.
    </p>
    <p style="color:var(--dim); font-size:12px;">
      This page will switch to the offline fallback when the instance goes down.
    </p>
  </div>
</div>
</body>
</html>
"""

# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ML Training Dashboard")
    parser.add_argument("--port", type=int, default=5000)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--spot-token",
                        default=os.environ.get("SPOT_TOKEN", ""),
                        help="Bearer token required for POST /api/spot-price")
    parser.add_argument("--telegram-webhook-secret",
                        default=os.environ.get("TELEGRAM_WEBHOOK_SECRET", ""),
                        help="Secret token for Telegram webhook validation")
    args = parser.parse_args()

    if args.spot_token:
        app.config["SPOT_TOKEN"] = args.spot_token
        print("  Spot-price POST auth: enabled")
    else:
        print("  Spot-price POST auth: disabled (no --spot-token)")

    if args.telegram_webhook_secret:
        app.config["TELEGRAM_WEBHOOK_SECRET"] = args.telegram_webhook_secret
        print("  Telegram webhook auth: enabled")
    else:
        print("  Telegram webhook auth: disabled (no --telegram-webhook-secret)")

    print(f"Starting dashboard on http://{args.host}:{args.port}")
    print(f"  Project dir: {PROJECT_DIR}")
    print(f"  Data dir:    {DATA_DIR}")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug,
            threaded=True)
