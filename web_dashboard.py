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
import time
import threading
import urllib.request
from datetime import datetime, timezone

import yaml
from flask import Flask, Response, jsonify, request, abort

# ── Configuration ────────────────────────────────────────────────────────────
PROJECT_DIR = "/home/ubuntu/KahnemanHybridExperiment"
DATA_DIR = "/opt/dlami/nvme/ml-lab"
EVAL_DIR = os.path.join(DATA_DIR, "eval_metrics")
CONFIG_PATH = os.path.join(PROJECT_DIR, "configs/tiny.yaml")
WANDB_DIR = os.path.join(PROJECT_DIR, "wandb")
CHECKPOINT_DIR = os.path.join(DATA_DIR, "checkpoints")
SPOT_PRICE_FILE = "/tmp/spot_price.json"
BOOTSTRAP_STATUS_FILE = "/tmp/bootstrap_status.json"

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
    if os.path.isdir(CHECKPOINT_DIR):
        checkpoints = sorted(os.listdir(CHECKPOINT_DIR))

    return {
        "trainer_running": is_running("joint_trainer"),
        "sync_running": is_running("sync-checkpoint"),
        "checkpoints": checkpoints,
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

    # ETA
    eta_s = None
    phase = "idle"
    if latest and len(steps) >= 2:
        elapsed = latest["elapsed_s"]
        sps = current_step / elapsed if elapsed > 0 else 0
        remaining = max_steps - current_step
        eta_s = remaining / sps if sps > 0 else None
        phase = "warmup" if current_step <= warmup_steps else "cosine_decay"

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

    # Projected totals
    od_projected = round(od_cost / current_step * max_steps, 2) if od_cost and current_step > 0 else None
    spot_projected = round(spot_cost / current_step * max_steps, 2) if spot_cost and current_step > 0 else None

    inst["ondemand_cost"] = od_cost
    inst["ondemand_projected"] = od_projected
    inst["spot_rate"] = spot_rate
    inst["spot_cost"] = spot_cost
    inst["spot_projected"] = spot_projected
    inst["spot_updated"] = spot_data.get("updated") if spot_data else None
    if od_cost and spot_cost:
        inst["savings"] = round(od_cost - spot_cost, 2)
        inst["savings_pct"] = round((1 - spot_cost / od_cost) * 100, 1)

    # Training time
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
        "gpu": gpu,
        "infra": infra,
        "milestones": milestones,
        "instance": inst,
        "bootstrap": cached("bootstrap", 2, read_bootstrap_status),
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


@app.route("/api/status")
def api_status():
    return jsonify(build_status())


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


@app.route("/")
def index():
    return HTML_PAGE


# ── Inline HTML/CSS/JS ────────────────────────────────────────────────────────

HTML_PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>ML Training Dashboard</title>
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
  color: var(--text);
  font-size: 13px;
  line-height: 1.5;
  overflow-x: hidden;
  min-width: 0;
}
.container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 12px;
  overflow: hidden;
}

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 10px 14px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
  gap: 8px;
}
.header h1 { font-size: 15px; font-weight: 600; white-space: nowrap; }
.header .meta { color: var(--dim); font-size: 11px; }
.header-links { display: flex; gap: 10px; font-size: 11px; }
.header-links a { color: var(--accent); text-decoration: none; white-space: nowrap; }
.header-links a:hover { text-decoration: underline; }
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
  font-size: 11px;
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
  font-size: 11px;
  font-weight: 600;
  color: #000;
  min-width: 36px;
}

/* Metric boxes */
.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(100px, 1fr));
  gap: 8px;
}
.metric-box {
  background: var(--bg);
  border-radius: 6px;
  padding: 10px 8px;
  text-align: center;
  min-width: 0;
  overflow: hidden;
}
.metric-box .label {
  font-size: 10px;
  color: var(--dim);
  margin-bottom: 3px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.metric-box .value {
  font-size: 18px;
  font-weight: 700;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.metric-box .sub { font-size: 10px; color: var(--dim); margin-top: 2px; }
.metric-box canvas { margin-top: 4px; }

/* Cost comparison layout */
/* Cost table */
.cost-tbl {
  width: 100%;
  border-collapse: collapse;
  font-size: 12px;
}
.cost-tbl th {
  font-size: 10px;
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
  font-size: 11px;
}
.cost-tbl .cost-accent { font-weight: 700; font-size: 14px; }
.cost-tbl .row-savings td { border-top: 1px solid var(--border); padding-top: 4px; }
.spot-stale { font-size: 10px; color: var(--orange); margin-top: 4px; }

/* Instance info row */
.inst-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  font-size: 11px;
}
.inst-row .inst-item { color: var(--dim); white-space: nowrap; }
.inst-row .inst-val { color: var(--text); font-weight: 600; }

/* GPU bars */
.bar-row { display: flex; align-items: center; gap: 8px; margin: 5px 0; }
.bar-label { width: 75px; font-size: 11px; color: var(--dim); flex-shrink: 0; }
.bar-outer {
  flex: 1; height: 16px; min-width: 0;
  background: var(--bg); border-radius: 3px; overflow: hidden;
}
.bar-inner {
  height: 100%; border-radius: 3px;
  transition: width 0.5s ease;
  display: flex; align-items: center; padding-left: 5px;
  font-size: 9px; font-weight: 600; color: #000;
}
.bar-val { width: 80px; text-align: right; font-size: 11px; flex-shrink: 0; white-space: nowrap; }

/* Badges */
.badge {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 10px;
  font-size: 11px;
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
  overflow-x: auto;
  font-size: 11px;
  line-height: 1.5;
  white-space: pre;
}
.log-box .eval-line { color: var(--yellow); }
.log-box .step-line { color: var(--text); }

/* Charts */
.chart-container { position: relative; height: 240px; }

/* Checkpoint list */
.ckpt-list { font-size: 11px; color: var(--dim); }
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
.bootstrap-panel.fading { opacity: 0; max-height: 0; overflow: hidden; padding: 0 14px; margin-bottom: 0; }
.bootstrap-panel h2 { font-size: 11px; text-transform: uppercase; letter-spacing: 0.1em; color: var(--dim); margin-bottom: 8px; }
.bs-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; }
.bs-header .bs-elapsed { font-size: 11px; color: var(--dim); }
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
  font-size: 11px;
  padding: 2px 0;
  white-space: nowrap;
  overflow: hidden;
}
.bs-step .bs-icon { width: 14px; text-align: center; flex-shrink: 0; }
.bs-step .bs-label { color: var(--dim); overflow: hidden; text-overflow: ellipsis; }
.bs-step .bs-time { color: var(--dim); font-size: 10px; margin-left: auto; flex-shrink: 0; }
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
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div><h1><span class="pulse" id="pulse"></span>ML Training Dashboard</h1></div>
    <div class="header-links">
      <a href="https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment" target="_blank">GitHub</a>
      <a href="https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment#readme" target="_blank">README</a>
      <a href="https://siliconstrategy.ai" target="_blank">siliconstrategy.ai</a>
    </div>
    <div class="meta">
      <span id="conn-status">Connecting...</span> &middot;
      <span id="timestamp"></span>
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
    <div style="display:flex; justify-content:space-between; flex-wrap:wrap; gap:6px; margin-bottom:4px; font-size:12px">
      <span>Step <strong id="cur-step">--</strong> / <span id="max-step">--</span></span>
      <span>Phase: <strong id="phase">--</strong></span>
      <span>Elapsed: <strong id="elapsed">--</strong></span>
      <span>Remaining: <strong id="eta">--</strong></span>
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
          <div class="label">LR</div>
          <div class="value" id="m-lr">--</div>
          <canvas id="spark-lr" width="100" height="28"></canvas>
        </div>
      </div>
    </div>

    <!-- GPU -->
    <div class="card">
      <h2>GPU</h2>
      <div id="gpu-name" style="color:var(--dim);font-size:11px;margin-bottom:6px">--</div>
      <div class="bar-row">
        <span class="bar-label">Utilization</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-util-bar" style="width:0%"></div></div>
        <span class="bar-val" id="gpu-util-val">--</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">VRAM</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-vram-bar" style="width:0%"></div></div>
        <span class="bar-val" id="gpu-vram-val">--</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">Temp</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-temp-bar" style="width:0%"></div></div>
        <span class="bar-val" id="gpu-temp-val">--</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">Power</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-power-bar" style="width:0%"></div></div>
        <span class="bar-val" id="gpu-power-val">--</span>
      </div>
    </div>

    <!-- Loss chart -->
    <div class="card">
      <h2>Loss Curves</h2>
      <div class="chart-container"><canvas id="chart-loss"></canvas></div>
    </div>

    <!-- Eval chart -->
    <div class="card">
      <h2>Eval Metrics</h2>
      <div class="chart-container"><canvas id="chart-eval"></canvas></div>
    </div>

    <!-- Instance & Cost -->
    <div class="card">
      <div style="display:flex; justify-content:space-between; align-items:baseline; flex-wrap:wrap; gap:6px; margin-bottom:8px">
        <h2 style="margin-bottom:0">Instance & Cost</h2>
        <div class="inst-row">
          <span class="inst-item"><span class="inst-val" id="inst-type">--</span></span>
          <span class="inst-item"><span class="inst-val" id="inst-lifecycle">--</span></span>
          <span class="inst-item"><span class="inst-val" id="inst-az">--</span></span>
          <span class="inst-item">up <span class="inst-val" id="inst-uptime">--</span></span>
        </div>
      </div>
      <table class="cost-tbl">
        <tr><th></th><th>Rate</th><th>Cost</th><th>Projected</th></tr>
        <tr>
          <td>On-Demand</td>
          <td id="od-rate">--</td>
          <td class="cost-accent" style="color:var(--orange)" id="od-cost">--</td>
          <td id="od-proj">--</td>
        </tr>
        <tr>
          <td>Spot</td>
          <td id="spot-rate">--</td>
          <td class="cost-accent" style="color:var(--green)" id="spot-cost">--</td>
          <td id="spot-proj">--</td>
        </tr>
        <tr class="row-savings">
          <td style="color:var(--green)">Savings</td>
          <td id="delta-pct" style="color:var(--green)">--</td>
          <td class="cost-accent" style="color:var(--green)" id="delta-cost">--</td>
          <td id="delta-proj" style="color:var(--green)">--</td>
        </tr>
      </table>
      <div class="spot-stale" id="spot-stale" style="display:none"></div>
    </div>

    <!-- Infra -->
    <div class="card">
      <h2>Infrastructure</h2>
      <div style="margin-bottom:6px">
        <span class="badge" id="badge-trainer">Trainer: ?</span>
        <span class="badge" id="badge-sync">Sync: ?</span>
      </div>
      <div style="margin-bottom:6px">
        <span style="font-size:11px;color:var(--dim)">Next milestones:</span>
        <div id="milestones" style="font-size:11px;margin-top:2px">--</div>
      </div>
      <div style="margin-bottom:6px">
        <span style="font-size:11px;color:var(--dim)">Checkpoints:</span>
        <div class="ckpt-list" id="ckpt-list">--</div>
      </div>
      <div>
        <span style="font-size:11px;color:var(--dim)">Config:</span>
        <div id="config-info" style="font-size:11px;color:var(--dim);margin-top:2px">--</div>
      </div>
    </div>

  </div>

  <!-- Log tail (full width, outside grid) -->
  <div class="card" style="margin-top:12px">
    <h2>Log Tail</h2>
    <div class="log-box" id="log-tail">--</div>
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
const sparkBuffers = { ar: [], diff: [], conf: [], lr: [] };
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
let lastEvalStep = null;
let lastChartRefresh = Date.now();
const CHART_REFRESH_INTERVAL = 300000; // 5 min

function checkChartRefresh(data) {
  const now = Date.now();
  let needsRefresh = false;

  // Refresh when new eval data appears
  const evalStep = data.latest_eval ? data.latest_eval.step : null;
  if (evalStep !== null && evalStep !== lastEvalStep) {
    lastEvalStep = evalStep;
    needsRefresh = true;
  }

  // Periodic refresh for loss chart (training data grows continuously)
  if (now - lastChartRefresh > CHART_REFRESH_INTERVAL) {
    needsRefresh = true;
  }

  if (needsRefresh) {
    lastChartRefresh = now;
    loadCharts();
  }
}

// ── Bootstrap panel ──────────────────────────────────────────────────────
let bsHideTimer = null;
let bsHidden = false;

function updateBootstrap(bs) {
  const panel = $('bootstrap-panel');
  if (!bs || bsHidden) {
    panel.classList.add('hidden');
    return;
  }
  panel.classList.remove('hidden');

  const steps = bs.steps || [];
  const doneCount = steps.filter(s => s.status === 'done').length;
  const total = steps.length || 1;
  const pct = (doneCount / total * 100).toFixed(0);

  // Progress bar
  const bar = $('bs-progress');
  bar.style.width = pct + '%';
  bar.className = 'bs-progress-inner' + (bs.status === 'done' ? ' done' : bs.status === 'failed' ? ' failed' : '');

  // Elapsed
  const elapsedEl = $('bs-elapsed');
  if (bs.status === 'done' && bs.total_elapsed_s != null) {
    elapsedEl.textContent = 'Completed in ' + fmtTimeLong(bs.total_elapsed_s);
  } else if (bs.total_elapsed_s != null) {
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

  // Auto-hide 30s after completion (never if failed)
  if (bs.status === 'done' && !bsHideTimer) {
    bsHideTimer = setTimeout(() => {
      panel.classList.add('fading');
      setTimeout(() => { panel.classList.add('hidden'); bsHidden = true; }, 800);
    }, 30000);
  }
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

function barColor(pct) {
  if (pct > 90) return '#f87171';
  if (pct > 70) return '#fbbf24';
  return '#34d399';
}

function $(id) { return document.getElementById(id); }

// ── UI updater ───────────────────────────────────────────────────────────
function updateUI(data) {
  $('timestamp').textContent = new Date(data.timestamp).toLocaleTimeString();

  // Bootstrap
  if (data.bootstrap) updateBootstrap(data.bootstrap);

  // Refresh charts when new eval data appears or every 5 min
  checkChartRefresh(data);

  // Progress
  $('cur-step').textContent = data.current_step.toLocaleString();
  $('max-step').textContent = data.max_steps.toLocaleString();
  $('phase').textContent = data.phase;
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
      staleEl.textContent = 'Run update-spot-price.sh to seed spot data';
    }

    // Savings row
    if (inst.savings != null) {
      $('delta-cost').textContent = '$' + inst.savings.toFixed(2);
      $('delta-pct').textContent = inst.savings_pct.toFixed(1) + '%';
    }
    if (inst.ondemand_projected != null && inst.spot_projected != null) {
      $('delta-proj').textContent = '$' + (inst.ondemand_projected - inst.spot_projected).toFixed(2);
    }
  }

  // Live metrics
  const t = data.latest_train;
  if (t) {
    $('m-ar-loss').textContent = t.ar_loss.toFixed(4);
    $('m-diff-loss').textContent = t.diff_loss.toFixed(4);
    $('m-conf-acc').textContent = (t.conf_acc * 100).toFixed(1) + '%';
    $('m-lr').textContent = t.lr.toExponential(2);

    sparkBuffers.ar.push(t.ar_loss);
    sparkBuffers.diff.push(t.diff_loss);
    sparkBuffers.conf.push(t.conf_acc);
    sparkBuffers.lr.push(t.lr);
    for (const k of Object.keys(sparkBuffers)) {
      if (sparkBuffers[k].length > SPARK_MAX) sparkBuffers[k].shift();
    }
    drawSparkline('spark-ar', sparkBuffers.ar, '#60a5fa');
    drawSparkline('spark-diff', sparkBuffers.diff, '#fb923c');
    drawSparkline('spark-conf', sparkBuffers.conf, '#34d399');
    drawSparkline('spark-lr', sparkBuffers.lr, '#a78bfa');
  }

  // GPU
  const g = data.gpu;
  if (g) {
    $('gpu-name').textContent = g.name;
    setBar('gpu-util', g.gpu_util, g.gpu_util.toFixed(0) + '%');
    setBar('gpu-vram', g.vram_used_mb / g.vram_total_mb * 100,
      (g.vram_used_mb/1024).toFixed(1) + '/' + (g.vram_total_mb/1024).toFixed(1) + ' GB');
    setBar('gpu-temp', g.temp_c, g.temp_c + 'C');
    setBar('gpu-power', g.power_w / g.power_limit_w * 100,
      g.power_w.toFixed(0) + '/' + g.power_limit_w.toFixed(0) + ' W');
  }

  // Infra
  const inf = data.infra;
  if (inf) {
    setBadge('badge-trainer', 'Trainer', inf.trainer_running);
    setBadge('badge-sync', 'Sync', inf.sync_running);
    const ckptEl = $('ckpt-list');
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

function setBar(prefix, pct, label) {
  pct = Math.min(100, Math.max(0, pct));
  const bar = $(prefix + '-bar');
  const val = $(prefix + '-val');
  bar.style.width = pct + '%';
  bar.style.background = barColor(pct);
  bar.textContent = pct > 20 ? label : '';
  val.textContent = label;
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
    sparkBuffers.conf = tail.map(h => h.conf_acc);
    sparkBuffers.lr = tail.map(h => h.lr);

    if (evals.length > 0) {
      evalChart.data.labels = evals.map(e => e.step);
      evalChart.data.datasets[0].data = evals.map(e => e.s1_tok_acc ?? e.s1_token_accuracy ?? null);
      evalChart.data.datasets[1].data = evals.map(e => e.conf_auroc ?? null);
      evalChart.data.datasets[2].data = evals.map(e => e.ar_ppl ?? e.ar_perplexity ?? null);
      evalChart.update();
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
    try { updateUI(JSON.parse(e.data)); } catch (err) { console.error('SSE parse error:', err); }
  };
  evtSource.onerror = () => {
    $('conn-status').textContent = 'Reconnecting...';
    $('pulse').style.background = '#f87171';
    evtSource.close();
    setTimeout(connectSSE, 5000);
  };
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

init();
</script>
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
    args = parser.parse_args()

    if args.spot_token:
        app.config["SPOT_TOKEN"] = args.spot_token
        print("  Spot-price POST auth: enabled")
    else:
        print("  Spot-price POST auth: disabled (no --spot-token)")

    print(f"Starting dashboard on http://{args.host}:{args.port}")
    print(f"  Project dir: {PROJECT_DIR}")
    print(f"  Data dir:    {DATA_DIR}")
    print()

    app.run(host=args.host, port=args.port, debug=args.debug,
            threaded=True)
