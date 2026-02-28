#!/usr/bin/env python3
"""
ML Training Dashboard — single-file Flask web UI.

Monitors training progress by reading log files and eval JSONs from disk.
No project-specific imports; configure the paths/regexes at the top.

Usage:
    pip install flask pyyaml
    python web_dashboard.py          # http://0.0.0.0:5000
    python web_dashboard.py --port 8080
"""

import argparse
import glob
import json
import os
import re
import subprocess
import time
import threading
from datetime import datetime, timezone

import yaml
from flask import Flask, Response, jsonify, request

# ── Configuration ────────────────────────────────────────────────────────────
PROJECT_DIR = "/home/ubuntu/KahnemanHybridExperiment"
DATA_DIR = "/opt/dlami/nvme/ml-lab"
EVAL_DIR = os.path.join(DATA_DIR, "eval_metrics")
CONFIG_PATH = os.path.join(PROJECT_DIR, "configs/tiny.yaml")
WANDB_DIR = os.path.join(PROJECT_DIR, "wandb")
CHECKPOINT_DIR = os.path.join(PROJECT_DIR, "checkpoints")

# Regex for training step lines:
#   step: 200 | ar_loss: 3.1444 | diff_loss: 7.2471 | conf_acc: 0.0000 | lr: 2.98e-05 | time: 609.7s
STEP_RE = re.compile(
    r"^step:\s*(?P<step>\d+)\s*\|"
    r"\s*ar_loss:\s*(?P<ar_loss>[\d.]+)\s*\|"
    r"\s*diff_loss:\s*(?P<diff_loss>[\d.]+)\s*\|"
    r"\s*conf_acc:\s*(?P<conf_acc>[\d.]+)\s*\|"
    r"\s*lr:\s*(?P<lr>[\d.eE+-]+)\s*\|"
    r"\s*time:\s*(?P<time>[\d.]+)s"
)

# Regex for eval lines:
#   [eval] step: 1000 | ar_ppl: 22004.99 | diff_loss: 6.8837 | s1_tok_acc: 0.0516 | ...
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
    """Parse all training step lines from the output log."""
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
    """Parse eval lines from the output log."""
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
    """Read eval_step_*.json files from the eval directory."""
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
    """Query nvidia-smi for GPU metrics."""
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
    """Check running processes and checkpoints."""
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
    """Read the training config YAML."""
    try:
        with open(CONFIG_PATH) as f:
            return yaml.safe_load(f)
    except Exception:
        return {}


def get_log_tail(n=20):
    """Return the last n lines of the output log."""
    log = find_output_log()
    if not log:
        return []
    try:
        with open(log, "r") as f:
            lines = f.readlines()
        return [l.rstrip() for l in lines[-n:]]
    except Exception:
        return []


# ── Composite status builder ─────────────────────────────────────────────────

def build_status():
    """Build the full status snapshot."""
    steps = cached("steps", 5, parse_training_steps)
    eval_lines = cached("eval_lines", 5, parse_eval_lines)
    eval_jsons = cached("eval_jsons", 15, read_eval_jsons)
    gpu = cached("gpu", 5, get_gpu_stats)
    infra = cached("infra", 10, get_infra_status)
    config = cached("config", 60, read_config)
    log_tail = get_log_tail(20)

    max_steps = config.get("training", {}).get("max_steps", 50000)
    warmup_steps = config.get("training", {}).get("warmup_steps", 2000)

    latest = steps[-1] if steps else None
    current_step = latest["step"] if latest else 0
    progress_pct = (current_step / max_steps * 100) if max_steps else 0

    # ETA calculation
    eta_s = None
    phase = "idle"
    if latest and len(steps) >= 2:
        elapsed = latest["elapsed_s"]
        sps = current_step / elapsed if elapsed > 0 else 0
        remaining = max_steps - current_step
        eta_s = remaining / sps if sps > 0 else None

        if current_step <= warmup_steps:
            phase = "warmup"
        else:
            phase = "cosine_decay"

    latest_eval = eval_lines[-1] if eval_lines else None

    return {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "current_step": current_step,
        "max_steps": max_steps,
        "progress_pct": round(progress_pct, 2),
        "phase": phase,
        "eta_seconds": round(eta_s, 0) if eta_s else None,
        "latest_train": latest,
        "latest_eval": latest_eval,
        "gpu": gpu,
        "infra": infra,
        "log_tail": log_tail,
        "config_summary": {
            "model": config.get("model", {}).get("name", "?"),
            "batch_size": config.get("training", {}).get("batch_size"),
            "grad_accum": config.get("training", {}).get("gradient_accumulation_steps"),
            "lr": config.get("training", {}).get("learning_rate"),
            "warmup_steps": warmup_steps,
            "max_steps": max_steps,
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
    # Merge log-based eval lines with on-disk JSONs, preferring JSONs (more fields)
    eval_jsons = cached("eval_jsons", 15, read_eval_jsons)
    eval_lines = cached("eval_lines", 5, parse_eval_lines)
    seen = {e.get("step") for e in eval_jsons}
    merged = list(eval_jsons)
    for e in eval_lines:
        if e["step"] not in seen:
            merged.append(e)
    merged.sort(key=lambda x: x.get("step", 0))
    return jsonify(merged)


@app.route("/stream")
def stream():
    def generate():
        while True:
            data = json.dumps(build_status())
            yield f"data: {data}\n\n"
            time.sleep(SSE_INTERVAL)
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
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--bg);
  color: var(--text);
  font-size: 13px;
  line-height: 1.5;
}
.container { max-width: 1400px; margin: 0 auto; padding: 16px; }

/* Header */
.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  margin-bottom: 16px;
}
.header h1 { font-size: 16px; font-weight: 600; }
.header .meta { color: var(--dim); font-size: 12px; }
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
  gap: 16px;
}
.grid-full { grid-column: 1 / -1; }

/* Cards */
.card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 16px;
}
.card h2 {
  font-size: 12px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--dim);
  margin-bottom: 12px;
}

/* Progress bar */
.progress-outer {
  width: 100%;
  height: 24px;
  background: var(--bg);
  border-radius: 4px;
  overflow: hidden;
  margin: 8px 0;
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
  min-width: 40px;
}

/* Metric boxes */
.metrics-row {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}
.metric-box {
  flex: 1;
  min-width: 120px;
  background: var(--bg);
  border-radius: 6px;
  padding: 12px;
  text-align: center;
}
.metric-box .label { font-size: 11px; color: var(--dim); margin-bottom: 4px; }
.metric-box .value { font-size: 20px; font-weight: 700; }
.metric-box .sub { font-size: 11px; color: var(--dim); margin-top: 2px; }
.metric-box canvas { margin-top: 6px; }

/* GPU bars */
.bar-row { display: flex; align-items: center; gap: 8px; margin: 6px 0; }
.bar-label { width: 80px; font-size: 12px; color: var(--dim); }
.bar-outer {
  flex: 1; height: 18px;
  background: var(--bg); border-radius: 3px; overflow: hidden;
}
.bar-inner {
  height: 100%; border-radius: 3px;
  transition: width 0.5s ease;
  display: flex; align-items: center; padding-left: 6px;
  font-size: 10px; font-weight: 600; color: #000;
}

/* Badges */
.badge {
  display: inline-block;
  padding: 3px 10px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  margin-right: 6px;
  margin-bottom: 4px;
}
.badge-green { background: var(--green); color: #000; }
.badge-red { background: var(--red); color: #000; }
.badge-dim { background: var(--border); color: var(--dim); }

/* Log */
.log-box {
  background: var(--bg);
  border-radius: 6px;
  padding: 10px;
  max-height: 300px;
  overflow-y: auto;
  font-size: 11px;
  line-height: 1.6;
  white-space: pre;
}
.log-box .eval-line { color: var(--yellow); }
.log-box .step-line { color: var(--text); }

/* Charts */
.chart-container { position: relative; height: 250px; }

/* Checkpoint list */
.ckpt-list { font-size: 12px; color: var(--dim); }
.ckpt-list span { display: inline-block; margin: 2px 4px; padding: 2px 6px; background: var(--bg); border-radius: 3px; }

/* Responsive */
@media (max-width: 800px) {
  .grid { grid-template-columns: 1fr; }
  .metrics-row { flex-direction: column; }
}
</style>
</head>
<body>
<div class="container">

  <!-- Header -->
  <div class="header">
    <div>
      <h1><span class="pulse" id="pulse"></span>ML Training Dashboard</h1>
    </div>
    <div class="meta">
      <span id="conn-status">Connecting...</span> &middot;
      <span id="timestamp">—</span>
    </div>
  </div>

  <!-- Progress -->
  <div class="card" style="margin-bottom:16px">
    <h2>Training Progress</h2>
    <div style="display:flex; justify-content:space-between; margin-bottom:4px">
      <span>Step <strong id="cur-step">—</strong> / <span id="max-step">—</span></span>
      <span>Phase: <strong id="phase">—</strong></span>
      <span>ETA: <strong id="eta">—</strong></span>
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
          <div class="value" id="m-ar-loss">—</div>
          <canvas id="spark-ar" width="100" height="30"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">Diff Loss</div>
          <div class="value" id="m-diff-loss">—</div>
          <canvas id="spark-diff" width="100" height="30"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">Conf Acc</div>
          <div class="value" id="m-conf-acc">—</div>
          <canvas id="spark-conf" width="100" height="30"></canvas>
        </div>
        <div class="metric-box">
          <div class="label">LR</div>
          <div class="value" id="m-lr">—</div>
          <canvas id="spark-lr" width="100" height="30"></canvas>
        </div>
      </div>
    </div>

    <!-- GPU -->
    <div class="card">
      <h2>GPU</h2>
      <div id="gpu-name" style="color:var(--dim);font-size:12px;margin-bottom:8px">—</div>
      <div class="bar-row">
        <span class="bar-label">Utilization</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-util-bar" style="width:0%"></div></div>
        <span id="gpu-util-val" style="width:40px;text-align:right">—</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">VRAM</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-vram-bar" style="width:0%"></div></div>
        <span id="gpu-vram-val" style="width:80px;text-align:right;font-size:12px">—</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">Temperature</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-temp-bar" style="width:0%"></div></div>
        <span id="gpu-temp-val" style="width:40px;text-align:right">—</span>
      </div>
      <div class="bar-row">
        <span class="bar-label">Power</span>
        <div class="bar-outer"><div class="bar-inner" id="gpu-power-bar" style="width:0%"></div></div>
        <span id="gpu-power-val" style="width:80px;text-align:right;font-size:12px">—</span>
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

    <!-- Infra -->
    <div class="card">
      <h2>Infrastructure</h2>
      <div style="margin-bottom:8px">
        <span class="badge" id="badge-trainer">Trainer: ?</span>
        <span class="badge" id="badge-sync">Sync: ?</span>
      </div>
      <div style="margin-bottom:8px">
        <strong style="font-size:12px;color:var(--dim)">Checkpoints:</strong>
        <div class="ckpt-list" id="ckpt-list">—</div>
      </div>
      <div>
        <strong style="font-size:12px;color:var(--dim)">Config:</strong>
        <div id="config-info" style="font-size:12px;color:var(--dim);margin-top:4px">—</div>
      </div>
    </div>

    <!-- Log tail -->
    <div class="card">
      <h2>Log Tail</h2>
      <div class="log-box" id="log-tail">—</div>
    </div>

  </div>
</div>

<script>
// ── Chart setup ──────────────────────────────────────────────────────────
const chartOpts = {
  responsive: true,
  maintainAspectRatio: false,
  animation: { duration: 300 },
  plugins: { legend: { labels: { color: '#888', font: { size: 11, family: 'monospace' } } } },
  scales: {
    x: { ticks: { color: '#666', font: { size: 10 } }, grid: { color: '#1f2233' } },
    y: { ticks: { color: '#666', font: { size: 10 } }, grid: { color: '#1f2233' } },
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
      y: { ...chartOpts.scales.y, position: 'left', title: { display: true, text: 'Acc / AUROC', color: '#666' } },
      y1: { ...chartOpts.scales.y, position: 'right', title: { display: true, text: 'PPL', color: '#666' }, grid: { drawOnChartArea: false } },
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

// ── Format helpers ───────────────────────────────────────────────────────
function fmtTime(s) {
  if (s == null) return '—';
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

// ── UI updater ───────────────────────────────────────────────────────────
function updateUI(data) {
  // Timestamp
  document.getElementById('timestamp').textContent = new Date(data.timestamp).toLocaleTimeString();

  // Progress
  document.getElementById('cur-step').textContent = data.current_step.toLocaleString();
  document.getElementById('max-step').textContent = data.max_steps.toLocaleString();
  document.getElementById('phase').textContent = data.phase;
  document.getElementById('eta').textContent = fmtTime(data.eta_seconds);
  const pct = data.progress_pct;
  const bar = document.getElementById('progress-bar');
  bar.style.width = pct + '%';
  bar.textContent = pct.toFixed(1) + '%';

  // Live metrics
  const t = data.latest_train;
  if (t) {
    document.getElementById('m-ar-loss').textContent = t.ar_loss.toFixed(4);
    document.getElementById('m-diff-loss').textContent = t.diff_loss.toFixed(4);
    document.getElementById('m-conf-acc').textContent = (t.conf_acc * 100).toFixed(1) + '%';
    document.getElementById('m-lr').textContent = t.lr.toExponential(2);

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
    document.getElementById('gpu-name').textContent = g.name;
    const utilPct = g.gpu_util;
    const vramPct = (g.vram_used_mb / g.vram_total_mb * 100);
    const tempPct = (g.temp_c / 100 * 100);
    const powerPct = (g.power_w / g.power_limit_w * 100);

    setBar('gpu-util', utilPct, utilPct.toFixed(0) + '%');
    setBar('gpu-vram', vramPct, (g.vram_used_mb/1024).toFixed(1) + ' / ' + (g.vram_total_mb/1024).toFixed(1) + ' GB');
    setBar('gpu-temp', tempPct, g.temp_c + '°C');
    setBar('gpu-power', powerPct, g.power_w.toFixed(0) + ' / ' + g.power_limit_w.toFixed(0) + ' W');
  }

  // Infra
  const inf = data.infra;
  if (inf) {
    setBadge('badge-trainer', 'Trainer', inf.trainer_running);
    setBadge('badge-sync', 'Sync', inf.sync_running);
    const ckptEl = document.getElementById('ckpt-list');
    if (inf.checkpoints && inf.checkpoints.length > 0) {
      ckptEl.innerHTML = inf.checkpoints.map(c => '<span>' + c + '</span>').join(' ');
    } else {
      ckptEl.textContent = 'None yet';
    }
  }

  // Config
  const cfg = data.config_summary;
  if (cfg) {
    document.getElementById('config-info').textContent =
      cfg.model + ' | bs=' + cfg.batch_size + '×' + cfg.grad_accum +
      ' | lr=' + cfg.lr + ' | warmup=' + cfg.warmup_steps;
  }

  // Log tail
  const logEl = document.getElementById('log-tail');
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
  const bar = document.getElementById(prefix + '-bar');
  const val = document.getElementById(prefix + '-val');
  bar.style.width = pct + '%';
  bar.style.background = barColor(pct);
  bar.textContent = pct > 15 ? label : '';
  val.textContent = label;
}

function setBadge(id, name, running) {
  const el = document.getElementById(id);
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

    // Loss chart
    lossChart.data.labels = hist.map(h => h.step);
    lossChart.data.datasets[0].data = hist.map(h => h.ar_loss);
    lossChart.data.datasets[1].data = hist.map(h => h.diff_loss);
    lossChart.update();

    // Sparkline buffers from history
    const tail = hist.slice(-SPARK_MAX);
    sparkBuffers.ar = tail.map(h => h.ar_loss);
    sparkBuffers.diff = tail.map(h => h.diff_loss);
    sparkBuffers.conf = tail.map(h => h.conf_acc);
    sparkBuffers.lr = tail.map(h => h.lr);

    // Eval chart
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
    document.getElementById('conn-status').textContent = 'Live';
    document.getElementById('pulse').style.background = '#34d399';
    try {
      const data = JSON.parse(e.data);
      updateUI(data);
    } catch (err) {
      console.error('SSE parse error:', err);
    }
  };
  evtSource.onerror = () => {
    document.getElementById('conn-status').textContent = 'Reconnecting...';
    document.getElementById('pulse').style.background = '#f87171';
    evtSource.close();
    setTimeout(connectSSE, 5000);
  };
}

// ── Init ─────────────────────────────────────────────────────────────────
async function init() {
  // Initial load
  try {
    const res = await fetch('/api/status');
    const data = await res.json();
    updateUI(data);
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
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    print(f"Starting dashboard on http://{args.host}:{args.port}")
    print(f"  Project dir: {PROJECT_DIR}")
    print(f"  Data dir:    {DATA_DIR}")
    app.run(host=args.host, port=args.port, debug=args.debug, threaded=True)
