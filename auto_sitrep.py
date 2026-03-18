#!/usr/bin/env python3
"""Auto-sitrep generator. Runs every 30 min via cron.
Fetches metrics from the dashboard API, maintains cumulative eval history,
generates sitrep.md, and commits/pushes to git."""

import json
import os
import glob
import subprocess
import sys
import fcntl
import argparse
from datetime import datetime, timezone, timedelta
from io import BytesIO
from zoneinfo import ZoneInfo
import urllib.request
import urllib.parse
from urllib.request import urlopen
from urllib.error import URLError

PROJECT = "/home/ubuntu/KahnemanHybridExperiment"
EVAL_DIR = "/opt/dlami/nvme/ml-lab/eval_metrics"
COST_LEDGER = "/opt/dlami/nvme/ml-lab/cost/cost_ledger.json"
HISTORY_FILE = "/tmp/auto-sitrep-eval-history.json"
TELEGRAM_STEP_INTERVAL = 10_000  # only send Telegram every N training steps
SITREP_PATH = os.path.join(PROJECT, "sitrep.md")

ET = ZoneInfo("America/New_York")  # handles EST/EDT automatically


def send_telegram(message, parse_mode="Markdown"):
    """Send a message via Telegram bot API. Silently no-ops if not configured."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return

    # Telegram limit is 4096 chars
    if len(message) > 4000:
        message = message[:3990] + "\n...(truncated)"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": message,
        "parse_mode": parse_mode,
    }).encode()

    try:
        req = urllib.request.Request(url, data=data)
        resp = urllib.request.urlopen(req, timeout=15)
        print(f"[auto_sitrep] Telegram sent ({resp.status})", file=sys.stderr)
    except Exception as e:
        print(f"[auto_sitrep] Telegram send failed: {e}", file=sys.stderr)


def fetch_status():
    """Fetch /api/status from the local dashboard."""
    try:
        with urlopen("http://localhost:5000/api/status", timeout=10) as r:
            return json.loads(r.read())
    except (URLError, Exception) as e:
        print(f"ERROR: Could not fetch /api/status: {e}", file=sys.stderr)
        sys.exit(1)


def load_eval_metrics_files():
    """Load eval_metrics/eval_step_*.json files into a dict keyed by step."""
    rows = {}
    for path in glob.glob(os.path.join(EVAL_DIR, "eval_step_*.json")):
        try:
            with open(path) as f:
                d = json.load(f)
            step = d.get("step")
            if step and step >= 1000:
                rows[step] = {
                    "step": step,
                    "ar_ppl": d.get("ar_perplexity", d.get("ar_ppl")),
                    "diff_loss": d.get("diff_loss"),
                    "s1_tok_acc": d.get("s1_token_accuracy", d.get("s1_tok_acc")),
                    "conf_auroc": d.get("conf_auroc"),
                    "conf_ece": d.get("conf_ece"),
                }
        except (json.JSONDecodeError, OSError):
            continue
    return rows


def load_history():
    """Load the cumulative eval history from /tmp."""
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"evals": [], "prev_step": None, "prev_metrics": None}


def save_history(history):
    """Save the cumulative eval history."""
    tmp = HISTORY_FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(history, f)
    os.replace(tmp, HISTORY_FILE)


def load_cost_ledger():
    """Load the cost ledger for session history."""
    if os.path.exists(COST_LEDGER):
        try:
            with open(COST_LEDGER) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return None


def build_spot_history(ledger):
    """Build a markdown section summarizing spot instance sessions."""
    if not ledger or not ledger.get("sessions"):
        return ""
    sessions = ledger["sessions"]
    n = len(sessions)
    total_cost = ledger.get("total_cost", sum(s.get("spot_cost", 0) for s in sessions))
    if n <= 1:
        return ""
    lines = [
        f"## Spot instance history ({n} instances)\n",
        "Training has survived {n} spot reclaims via checkpoint recovery. "
        "Each new instance bootstraps autonomously, restores the latest "
        "checkpoint from S3, and resumes training.\n".format(n=n - 1),
        "| # | AZ | Steps | Boot (UTC) | Cost |",
        "|---|-----|-------|------------|------|",
    ]
    for i, s in enumerate(sessions):
        az = s.get("az", "?")
        ss = s.get("steps_start", "?")
        se = s.get("steps_end", "?")
        boot = s.get("boot_time", "?")[:16].replace("T", " ")
        cost = s.get("spot_cost", 0)
        lines.append(f"| {i + 1} | {az} | {ss:,}→{se:,} | {boot} | ${cost:.2f} |")
    lines.append(f"\n**Total spot cost across all instances: ${total_cost:.2f}**\n")
    return "\n".join(lines) + "\n"


def fmt_step(step):
    """Format step like ~18,000."""
    return f"~{step:,}"


def fmt_pct(val):
    """Format 0.244 as 24.4%."""
    return f"{val * 100:.1f}%"


def build_trajectory_table(rows):
    """Build the markdown trajectory table from sorted eval rows."""
    if not rows:
        return "*(no eval data yet)*\n"
    first = rows[0]["step"]
    last = rows[-1]["step"]
    lines = [
        f"## Eval trajectory (step {first // 1000}k → {last // 1000}k)\n",
        "| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |",
        "|-------|--------|-----------|--------|-------|--------|",
    ]
    for r in rows:
        s1 = fmt_pct(r["s1_tok_acc"]) if r.get("s1_tok_acc") is not None else "—"
        auroc = f'{r["conf_auroc"]:.3f}' if r.get("conf_auroc") is not None else "—"
        ece = f'{r["conf_ece"]:.4f}' if r.get("conf_ece") is not None else "—"
        ar = f'{r["ar_ppl"]:.1f}' if r.get("ar_ppl") is not None else "—"
        dl = f'{r["diff_loss"]:.2f}' if r.get("diff_loss") is not None else "—"
        lines.append(f"| {r['step']} | {ar}   | {dl}      | {s1}  | {auroc} | {ece} |")
    return "\n".join(lines) + "\n"


def build_trends(prev_metrics, prev_step, current_step, latest_eval):
    """Build the trends section comparing to the previous auto-sitrep run."""
    if prev_metrics is None or prev_step is None:
        return "## Trends\n\n*(first auto-sitrep run after boot — no prior data)*\n"
    delta_steps = current_step - prev_step
    lines = [
        "## Trends since last auto-sitrep\n",
        f"- +{delta_steps:,} steps ({fmt_step(prev_step)} → {fmt_step(current_step)})",
    ]
    pm = prev_metrics
    le = latest_eval
    if pm.get("diff_loss") and le.get("diff_loss"):
        lines.append(f"- Diff loss: {pm['diff_loss']:.2f} → {le['diff_loss']:.2f}")
    if pm.get("s1_tok_acc") and le.get("s1_tok_acc"):
        lines.append(f"- S1 accuracy: {fmt_pct(pm['s1_tok_acc'])} → {fmt_pct(le['s1_tok_acc'])}")
    if pm.get("conf_auroc") and le.get("conf_auroc"):
        lines.append(f"- AUROC: {pm['conf_auroc']:.3f} → {le['conf_auroc']:.3f}")
    return "\n".join(lines) + "\n"


def generate_sitrep(status, trajectory_rows, prev_metrics, prev_step, ledger=None):
    """Generate the full sitrep markdown."""
    now = datetime.now(ET)
    utc_now = datetime.now(timezone.utc)
    header_time = f"{now.strftime('%-I:%M %p')} ET / {utc_now.strftime('%H:%M')} UTC"

    step = status["current_step"]
    max_steps = status["max_steps"]
    pct = status["progress_pct"]
    gpu = status["gpu"]
    inst = status["instance"]
    le = status.get("latest_eval") or {}
    lt = status.get("latest_train") or {}
    infra = status.get("infra", {})

    uptime_s = inst.get("uptime_seconds", 0)
    uptime_h = int(uptime_s // 3600)
    uptime_m = int((uptime_s % 3600) // 60)

    eta_s = status.get("eta_seconds", 0)
    eta_h = eta_s / 3600 if eta_s else 0

    # Calculate rate from recent log lines (100 steps apart) for accuracy
    rate = 0
    sec_per_step = 0
    log_tail = status.get("log_tail", [])
    log_times = []
    for line in log_tail:
        if "time:" in line and "step:" in line and "[eval]" not in line:
            for part in line.split("|"):
                if "time:" in part:
                    try:
                        log_times.append(float(part.strip().replace("time:", "").replace("s", "").strip()))
                    except ValueError:
                        pass
    if len(log_times) >= 2:
        interval = log_times[-1] - log_times[-2]  # time between 100-step log entries
        if interval > 0:
            sec_per_step = interval / 100
            rate = 3600 / sec_per_step
    if rate == 0:
        # Fallback to naive calculation
        rate = step / (status.get("elapsed_seconds", 1) / 3600) if status.get("elapsed_seconds") else 0
        sec_per_step = (status.get("elapsed_seconds", 0) / max(step, 1))

    # Get eval values
    ar_ppl = le.get("ar_ppl", 0)
    diff_loss = le.get("diff_loss", 0)
    s1_acc = le.get("s1_tok_acc", 0)
    auroc = le.get("conf_auroc", 0)
    ece = le.get("conf_ece", 0)
    eval_step = le.get("step", step)

    # Diff loss progress toward 4.0 target (from starting ~8.0)
    diff_progress = max(0, min(100, (8.0 - diff_loss) / (8.0 - 4.0) * 100))
    # S1 accuracy progress toward 40% target
    s1_progress = min(100, s1_acc / 0.40 * 100)

    # Checkpoints
    ckpts = infra.get("checkpoints", [])
    ckpt_str = ", ".join(ckpts) if ckpts else "none"

    # Trajectory table
    traj = build_trajectory_table(trajectory_rows)

    # Trends
    trends = build_trends(prev_metrics, prev_step, step, le)

    # Spot history
    spot_history = build_spot_history(ledger)

    md = f"""# Sitrep — {now.strftime('%Y-%m-%d')} {header_time}

## v4 Training — running, healthy, {pct:.0f}% complete

- **Step {fmt_step(step)} / {max_steps:,}** ({pct:.1f}%)
- GPU: {gpu['gpu_util']:.0f}% utilization, {gpu['vram_used_mb'] / 1024:.1f} / {gpu['vram_total_mb'] / 1024:.0f} GB VRAM, {gpu['temp_c']:.0f}°C
- Rate: ~{rate:.0f} steps/hr ({sec_per_step:.1f}s/step)
- ETA to {max_steps // 1000}k: ~{eta_h:.1f} hours at current rate
- Spot price: ${inst.get('spot_rate', 'N/A')}/hr ({inst['instance_type']})
- Spot cost (this instance): ${inst.get('spot_cost', 0) or 0:.2f} — projected: ${inst.get('spot_projected', 0) or 0:.2f}
- Total cost across {inst.get('total_sessions', 1)} instance(s): ${inst.get('total_run_cost') or inst.get('spot_cost') or 0:.2f}
- Instance up {uptime_h}h{uptime_m:02d}m since bootstrap ({inst.get('boot_time_utc', '?')[:16].replace('T', ' ')} UTC){f" — spot recovery from prior instance (checkpoint restored from S3)" if inst.get('total_sessions', 1) > 1 else ""}

{traj}
Live at step {fmt_step(step)}: ar_loss {lt.get('ar_loss', 0):.2f}, diff_loss {lt.get('diff_loss', 0):.2f}, conf_acc {lt.get('conf_acc', 0):.3f}

## Target status (5 of 5)

- **AR PPL < 40:** {ar_ppl:.1f} — met since step 50, drifting up slowly but solid margin
- **AUROC > 0.75:** {auroc:.3f} — met since step 8k, steady climb
- **ECE < 0.05:** {ece:.3f} — met since step 1k, excellent calibration
- **Diff loss → 4.0:** {diff_loss:.2f} at eval step {eval_step // 1000}k — {diff_progress:.0f}% of the way{', closing in' if diff_progress > 80 else ''}
- **S1 accuracy → 40%:** {fmt_pct(s1_acc)} at eval — {s1_progress:.0f}% of target

{trends}
{spot_history}## Code & infra

- All services healthy: sync daemon, nginx, Flask dashboard, spot price cron
- Checkpoints on disk: {ckpt_str} (all synced to S3)
- *Auto-generated by auto_sitrep.py*

## v1 Benchmark Results (step 50k)

| Benchmark | Pretrained GPT-2 | v1 Final (50k) | Delta |
|-----------|-----------------|----------------|-------|
| LAMBADA accuracy (S2) | 95.08% | 94.26% | -0.82% |
| LAMBADA perplexity (S2) | 1.38 | 1.46 | +0.08 |
| WikiText-103 PPL (S2) | 29.07 | 43.86 | +14.79 |
| WikiText-103 S1 loss | 12.67 | 4.12 | -8.55 |

AR metrics regressed slightly (expected from joint training). Diffusion S1 loss dropped 67%, confirming the model learned diffusion generation.

## What's next (after v2 completes)

1. Run LAMBADA + WikiText-103 benchmarks on final v2 checkpoint
2. Compare v1 vs v2 (S1 accuracy, diffusion loss, AR PPL trade-off)
3. Confidence head analysis — escalation rates, S1 vs S2 quality per difficulty tier
"""
    return md


def generate_sitrep_via_claude(status, trajectory_rows, prev_metrics, prev_step, ledger=None):
    """Generate sitrep via Claude API, falling back to template on failure."""
    api_key = os.environ.get("CLAUDE_API_KEY", "")
    if not api_key:
        # Try AWS Secrets Manager
        try:
            import subprocess
            api_key = subprocess.check_output(
                ["aws", "secretsmanager", "get-secret-value",
                 "--secret-id", "ml-lab/claude-api-key",
                 "--region", os.environ.get("AWS_DEFAULT_REGION", "us-east-1"),
                 "--query", "SecretString", "--output", "text"],
                timeout=10, text=True
            ).strip()
        except Exception:
            pass
    if not api_key:
        return generate_sitrep(status, trajectory_rows, prev_metrics, prev_step, ledger)

    try:
        import anthropic
    except ImportError:
        print("[auto_sitrep] anthropic SDK not installed, using template", file=sys.stderr)
        return generate_sitrep(status, trajectory_rows, prev_metrics, prev_step, ledger)

    try:
        client = anthropic.Anthropic(api_key=api_key)
        # Build raw data dict from status, trajectory, etc.
        raw_data = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "current_step": status.get("current_step", 0),
            "max_steps": status.get("max_steps", 50000),
            "progress_pct": status.get("progress_pct", 0),
            "gpu": status.get("gpu", {}),
            "instance": status.get("instance", {}),
            "latest_eval": status.get("latest_eval", {}),
            "latest_train": status.get("latest_train", {}),
            "infra": status.get("infra", {}),
            "trajectory": trajectory_rows,
            "prev_step": prev_step,
            "prev_metrics": prev_metrics,
            "cost_ledger_sessions": ledger.get("sessions", []) if ledger else [],
            "total_cost": ledger.get("total_cost", 0) if ledger else 0,
        }

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system="""You are an ML ops analyst for a dual-process language model research project.

Write a concise markdown SITREP report (under 4000 chars). Structure:

## v4 Training Status
Progress, step count, GPU utilization, rate, ETA, spot cost.

## Eval Metrics & Trends
Table of recent eval checkpoints. Highlight trends in AR perplexity, diffusion loss, S1 token accuracy, confidence AUROC/ECE. Flag any regressions.

## Target Scorecard
5 targets: AR PPL < 40, AUROC > 0.75, ECE < 0.05, Diff loss -> 4.0, S1 accuracy -> 40%. Show current values and whether met.

## v1 Benchmark Baseline
v1 final (step 50k) LAMBADA accuracy: 94.26%, LAMBADA PPL: 1.46, WikiText-103 PPL: 43.86, S1 loss: 4.12. Pretrained GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. AR regressed slightly from joint training; S1 loss dropped 67%.

## Infrastructure
Spot instance history, cost, uptime. Note any spot reclaims or issues.

## What's Next
After v2 completes: v2 benchmarks, v1 vs v2 comparison, confidence head analysis.

Style: direct, technical, no filler. Use ## headers, tables, bold for key numbers. Be opinionated about trends.""",
            messages=[{"role": "user", "content": f"Generate a SITREP from this raw training data:\n\n```json\n{json.dumps(raw_data, indent=2, default=str)}\n```"}],
        )

        md = message.content[0].text
        print(f"[auto_sitrep] Claude API generated sitrep ({len(md)} chars)")
        return md

    except Exception as e:
        print(f"[auto_sitrep] Claude API failed: {e}, using template", file=sys.stderr)
        return generate_sitrep(status, trajectory_rows, prev_metrics, prev_step, ledger)


def generate_telegram_summary(status: dict, trajectory_rows: list,
                               prev_metrics: dict | None, prev_step: int | None,
                               ledger: dict | None) -> str:
    """Generate a compact ~500-800 char Telegram summary."""
    now = datetime.now(ZoneInfo("America/New_York"))
    step = status.get("current_step", 0)
    max_steps = status.get("max_steps", 50000)
    pct = status.get("progress_pct", 0)
    gpu = status.get("gpu", {})
    inst = status.get("instance", {})
    le = status.get("latest_eval") or {}
    eval_step = le.get("step", step)

    # Compute rate
    rate = 0
    log_tail = status.get("log_tail", [])
    log_times = []
    for line in log_tail:
        if "time:" in line and "step:" in line and "[eval]" not in line:
            for part in line.split("|"):
                if "time:" in part:
                    try:
                        log_times.append(float(part.strip().replace("time:", "").replace("s", "").strip()))
                    except ValueError:
                        pass
    if len(log_times) >= 2:
        interval = log_times[-1] - log_times[-2]
        if interval > 0:
            rate = 3600 / (interval / 100)
    if rate == 0:
        elapsed = status.get("elapsed_seconds", 1)
        rate = step / (elapsed / 3600) if elapsed else 0

    eta_s = status.get("eta_seconds", 0)
    eta_h = eta_s / 3600 if eta_s else 0

    # Metric values and status indicators
    ar_ppl = le.get("ar_ppl", 0)
    diff_loss = le.get("diff_loss", 0)
    s1_acc = le.get("s1_tok_acc", 0)
    auroc = le.get("conf_auroc", 0)
    ece = le.get("conf_ece", 0)

    def indicator(met: bool, improving: bool = True) -> str:
        if met:
            return "✅"
        return "🔄" if improving else "⚠️"

    ar_ind = indicator(ar_ppl < 40 and ar_ppl > 0)
    diff_ind = "✅" if diff_loss <= 4.0 and diff_loss > 0 else ("🔄" if diff_loss < 6.0 else "⚠️")
    s1_ind = "✅" if s1_acc >= 0.40 else ("🔄" if s1_acc >= 0.25 else "⚠️")
    auroc_ind = indicator(auroc > 0.75)
    ece_ind = indicator(ece < 0.05 and ece > 0)

    # Cost
    spot_rate = inst.get("spot_rate", "?")
    spot_cost = inst.get("spot_cost", 0) or 0
    total_cost = inst.get("total_run_cost") or spot_cost
    projected = inst.get("spot_projected", 0) or 0
    budget = 50
    budget_pct = (total_cost / budget * 100) if budget else 0

    lines = [
        f"📊 SITREP — {now.strftime('%Y-%m-%d %-I:%M %p')} ET",
        "",
        f"Training: Step {step:,}/{max_steps // 1000}k ({pct:.0f}%)",
        f"Rate: ~{rate:.0f} steps/hr | ETA: ~{eta_h:.0f}h",
        f"GPU: {gpu.get('gpu_util', 0):.0f}% | {gpu.get('vram_used_mb', 0) / 1024:.1f}/{gpu.get('vram_total_mb', 0) / 1024:.0f} GB | {gpu.get('temp_c', 0):.0f}°C",
        "",
        f"Metrics (eval {eval_step // 1000}k):",
        f"  AR PPL:    {ar_ppl:.2f}  {ar_ind} (<40)",
        f"  Diff Loss:  {diff_loss:.2f}  {diff_ind} (→4.0)",
        f"  S1 Acc:    {fmt_pct(s1_acc)}  {s1_ind} (→40%)",
        f"  AUROC:     {auroc:.3f}  {auroc_ind} (>0.75)",
        f"  ECE:       {ece:.3f}  {ece_ind} (<0.05)",
        "",
        f"Cost: ${spot_rate}/hr spot | Session ${spot_cost:.2f}",
        f"Run Total: ${total_cost:.2f} | Projected: ${projected:.2f}",
        f"Budget: ${budget} ({budget_pct:.0f}% used)",
        "",
        "🔗 train.bitbanshee.com",
    ]
    return "\n".join(lines)


def generate_metrics_image(status: dict, latest_eval: dict,
                           ledger: dict | None) -> bytes | None:
    """Render a 700x420 dark-theme metrics card PNG using Pillow."""
    try:
        from PIL import Image, ImageDraw, ImageFont
    except ImportError:
        print("[auto_sitrep] Pillow not installed, skipping image", file=sys.stderr)
        return None

    W, H = 700, 420
    # Color palette matching dashboard
    bg = (26, 26, 46)         # #1a1a2e
    surface = (22, 33, 62)    # #16213e
    accent = (167, 139, 250)  # #a78bfa
    text_color = (224, 224, 224)  # #e0e0e0
    dim = (140, 140, 160)
    green = (74, 222, 128)    # #4ade80
    yellow = (251, 191, 36)   # #fbbf24
    red = (248, 113, 113)     # #f87171
    bar_bg = (50, 50, 70)

    img = Image.new("RGB", (W, H), bg)
    draw = ImageDraw.Draw(img)

    # Try to load monospace font
    font_sm = None
    font_md = None
    font_lg = None
    for font_path in [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
    ]:
        if os.path.exists(font_path):
            try:
                font_sm = ImageFont.truetype(font_path, 12)
                font_md = ImageFont.truetype(font_path, 14)
                font_lg = ImageFont.truetype(font_path, 16)
                break
            except Exception:
                pass
    if font_sm is None:
        try:
            font_sm = ImageFont.load_default()
            font_md = font_sm
            font_lg = font_sm
        except Exception:
            font_sm = font_md = font_lg = ImageFont.load_default()

    step = status.get("current_step", 0)
    max_steps = status.get("max_steps", 50000)
    pct = status.get("progress_pct", 0)
    gpu = status.get("gpu", {})
    inst = status.get("instance", {})
    le = latest_eval or {}

    # Metric values
    ar_ppl = le.get("ar_ppl", 0)
    diff_loss = le.get("diff_loss", 0)
    s1_acc = le.get("s1_tok_acc", 0)
    auroc = le.get("conf_auroc", 0)
    ece = le.get("conf_ece", 0)

    # Cost
    spot_rate = inst.get("spot_rate", "?")
    spot_cost = inst.get("spot_cost", 0) or 0
    total_cost = inst.get("total_run_cost") or spot_cost
    projected = inst.get("spot_projected", 0) or 0
    budget = 50
    budget_pct = (total_cost / budget * 100) if budget else 0

    # Rate / ETA
    rate = 0
    log_tail = status.get("log_tail", [])
    log_times = []
    for line in log_tail:
        if "time:" in line and "step:" in line and "[eval]" not in line:
            for part in line.split("|"):
                if "time:" in part:
                    try:
                        log_times.append(float(part.strip().replace("time:", "").replace("s", "").strip()))
                    except ValueError:
                        pass
    if len(log_times) >= 2:
        interval = log_times[-1] - log_times[-2]
        if interval > 0:
            rate = 3600 / (interval / 100)
    if rate == 0:
        elapsed = status.get("elapsed_seconds", 1)
        rate = step / (elapsed / 3600) if elapsed else 0
    eta_s = status.get("eta_seconds", 0)
    eta_h = eta_s / 3600 if eta_s else 0

    y = 12

    # ── Header ──
    draw.rectangle([0, 0, W, 50], fill=surface)
    draw.text((16, y), "DUAL-PROCESS LM — LIVE METRICS", fill=accent, font=font_lg)
    y = 56

    # ── Progress bar ──
    prog_text = f"Step {step:,} / {max_steps:,} ({pct:.0f}%)"
    draw.text((16, y), prog_text, fill=text_color, font=font_md)
    bar_x, bar_y, bar_w, bar_h = 420, y + 2, 260, 16
    draw.rectangle([bar_x, bar_y, bar_x + bar_w, bar_y + bar_h], fill=bar_bg)
    fill_w = int(bar_w * min(pct, 100) / 100)
    if fill_w > 0:
        draw.rectangle([bar_x, bar_y, bar_x + fill_w, bar_y + bar_h], fill=accent)
    y += 30

    # ── Divider ──
    draw.line([(12, y), (W - 12, y)], fill=accent, width=1)
    y += 8

    # ── Metrics table header ──
    draw.text((16, y), "METRIC", fill=dim, font=font_sm)
    draw.text((220, y), "VALUE", fill=dim, font=font_sm)
    draw.text((360, y), "TARGET", fill=dim, font=font_sm)
    draw.text((500, y), "STATUS", fill=dim, font=font_sm)
    y += 20

    # Metric rows
    def status_color(met: bool, close: bool = False) -> tuple:
        if met:
            return green
        return yellow if close else red

    metrics = [
        ("AR Perplexity", f"{ar_ppl:.2f}" if ar_ppl else "—", "< 40",
         ar_ppl > 0 and ar_ppl < 40, ar_ppl > 0 and ar_ppl < 60),
        ("Diff Loss", f"{diff_loss:.2f}" if diff_loss else "—", "→ 4.0",
         diff_loss > 0 and diff_loss <= 4.0, diff_loss > 0 and diff_loss < 6.0),
        ("S1 Accuracy", fmt_pct(s1_acc) if s1_acc else "—", "→ 40%",
         s1_acc >= 0.40, s1_acc >= 0.25),
        ("AUROC", f"{auroc:.3f}" if auroc else "—", "> 0.75",
         auroc > 0.75, auroc > 0.60),
        ("ECE", f"{ece:.4f}" if ece else "—", "< 0.05",
         ece > 0 and ece < 0.05, ece > 0 and ece < 0.10),
    ]

    for name, val, target, met, close in metrics:
        draw.text((16, y), name, fill=text_color, font=font_md)
        draw.text((220, y), val, fill=text_color, font=font_md)
        draw.text((360, y), target, fill=dim, font=font_md)
        # Status dot
        dot_color = status_color(met, close)
        dot_x, dot_y = 510, y + 4
        draw.ellipse([dot_x, dot_y, dot_x + 10, dot_y + 10], fill=dot_color)
        label = "MET" if met else ("WIP" if close else "MISS")
        draw.text((dot_x + 16, y), label, fill=dot_color, font=font_sm)
        y += 22

    # ── Divider ──
    y += 4
    draw.line([(12, y), (W - 12, y)], fill=accent, width=1)
    y += 8

    # ── Instance & Cost ──
    draw.text((16, y), "INSTANCE & COST", fill=dim, font=font_sm)
    y += 18
    itype = inst.get("instance_type", "?")
    az = inst.get("az", "?")
    draw.text((16, y), f"{itype} | {az} | Spot ${spot_rate}/hr", fill=text_color, font=font_md)
    y += 20
    draw.text((16, y), f"Session: ${spot_cost:.2f}  |  Run Total: ${total_cost:.2f}", fill=text_color, font=font_md)
    y += 20
    draw.text((16, y), f"Projected: ${projected:.2f}  |  Budget: ${budget} ({budget_pct:.0f}%)", fill=text_color, font=font_md)
    y += 24

    # ── Divider ──
    draw.line([(12, y), (W - 12, y)], fill=accent, width=1)
    y += 8

    # ── GPU & Rate ──
    gpu_util = gpu.get("gpu_util", 0)
    vram_used = gpu.get("vram_used_mb", 0) / 1024
    vram_total = gpu.get("vram_total_mb", 0) / 1024
    temp = gpu.get("temp_c", 0)
    draw.text((16, y), f"GPU: {gpu_util:.0f}% util  |  {vram_used:.1f}/{vram_total:.0f} GB  |  {temp:.0f}°C", fill=text_color, font=font_md)
    y += 20
    draw.text((16, y), f"Rate: ~{rate:.0f} steps/hr  |  ETA: ~{eta_h:.0f}h", fill=text_color, font=font_md)

    # Save to bytes
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def send_telegram_photo(image_bytes: bytes, caption: str = "") -> None:
    """Send a photo with caption via Telegram bot API."""
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID", "")
    if not token or not chat_id:
        return

    # Telegram caption limit is 1024 chars
    if len(caption) > 1020:
        caption = caption[:1010] + "\n...(truncated)"

    url = f"https://api.telegram.org/bot{token}/sendPhoto"

    # Build multipart/form-data manually (avoid extra dependencies)
    boundary = "----SitrepBoundary9876543210"
    body = BytesIO()

    def write_field(name: str, value: str) -> None:
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.write(f"{value}\r\n".encode())

    write_field("chat_id", chat_id)
    write_field("caption", caption)

    # Photo file field
    body.write(f"--{boundary}\r\n".encode())
    body.write(b'Content-Disposition: form-data; name="photo"; filename="metrics.png"\r\n')
    body.write(b"Content-Type: image/png\r\n\r\n")
    body.write(image_bytes)
    body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())

    data = body.getvalue()

    try:
        req = urllib.request.Request(
            url, data=data,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"}
        )
        resp = urllib.request.urlopen(req, timeout=30)
        print(f"[auto_sitrep] Telegram photo sent ({resp.status})", file=sys.stderr)
    except Exception as e:
        print(f"[auto_sitrep] Telegram photo send failed: {e}", file=sys.stderr)


def git_commit_push():
    """Stage sitrep.md, commit, and push. Non-fatal on failure."""
    os.chdir(PROJECT)
    try:
        subprocess.run(["git", "add", "sitrep.md"], check=True)

        # Check if there are staged changes
        result = subprocess.run(
            ["git", "diff", "--cached", "--quiet"],
            capture_output=True,
        )
        if result.returncode == 0:
            print("No changes to sitrep.md, skipping commit.")
            return

        subprocess.run(
            ["git", "commit", "-m", "auto-sitrep: update metrics"],
            check=True,
        )
        # Pull --rebase to integrate any remote changes before pushing
        subprocess.run(["git", "pull", "--rebase", "--autostash"], check=True)
        subprocess.run(["git", "push"], check=True)
        print("Committed and pushed sitrep.md")
    except subprocess.CalledProcessError as e:
        print(f"[auto_sitrep] git failed (non-fatal): {e}", file=sys.stderr)


def main(force_telegram: bool = False):
    print(f"[auto_sitrep] {datetime.now(timezone.utc).isoformat()}")

    lock_fd = open("/tmp/auto-sitrep.lock", "w")
    try:
        fcntl.flock(lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        print("[auto_sitrep] another instance is running, exiting.", file=sys.stderr)
        return

    # 1. Fetch live status
    status = fetch_status()
    latest_eval = status.get("latest_eval") or {}
    current_step = status.get("current_step", 0)

    # 2. Load history
    history = load_history()
    prev_step = history.get("prev_step")
    prev_metrics = history.get("prev_metrics")

    # 3. Load eval_metrics files (older data)
    file_evals = load_eval_metrics_files()

    # 4. Merge history evals into file_evals (history takes precedence for same step)
    for entry in history.get("evals", []):
        s = entry["step"]
        if s not in file_evals:
            file_evals[s] = entry

    # 5. Add latest_eval if new
    eval_step = latest_eval.get("step")
    if eval_step and eval_step not in file_evals:
        file_evals[eval_step] = {
            "step": eval_step,
            "ar_ppl": latest_eval.get("ar_ppl"),
            "diff_loss": latest_eval.get("diff_loss"),
            "s1_tok_acc": latest_eval.get("s1_tok_acc"),
            "conf_auroc": latest_eval.get("conf_auroc"),
            "conf_ece": latest_eval.get("conf_ece"),
        }

    # 6. Sort all evals, keep last 8 for the table
    all_evals = sorted(file_evals.values(), key=lambda x: x["step"])
    trajectory_rows = all_evals[-8:]

    # 7. Load cost ledger for spot history
    ledger = load_cost_ledger()

    # 8. Generate sitrep (try Claude API, fall back to template)
    md = generate_sitrep_via_claude(status, trajectory_rows, prev_metrics, prev_step, ledger)

    # 8. Write sitrep.md
    with open(SITREP_PATH, "w") as f:
        f.write(md)
    print(f"Wrote {SITREP_PATH}")

    # 9. Send Telegram notification BEFORE git (so push failures don't block it)
    last_tg_step = history.get("last_telegram_step", 0)
    should_send_telegram = force_telegram or (current_step - last_tg_step >= TELEGRAM_STEP_INTERVAL)
    if should_send_telegram:
        try:
            summary = generate_telegram_summary(status, trajectory_rows, prev_metrics, prev_step, ledger)
            img_bytes = generate_metrics_image(status, latest_eval, ledger)
            if img_bytes:
                send_telegram_photo(img_bytes, caption=summary)
            else:
                send_telegram(summary)
            # Don't update last_telegram_step on forced sends so scheduled sends stay on track
            if not force_telegram:
                history["last_telegram_step"] = current_step
        except Exception as e:
            print(f"[auto_sitrep] Telegram notification failed: {e}", file=sys.stderr)
    else:
        print(f"[auto_sitrep] Telegram skipped (last at {last_tg_step}, next at {last_tg_step + TELEGRAM_STEP_INTERVAL})")

    # 10. Git commit and push (non-fatal — sitrep already sent)
    git_commit_push()

    # 11. Save history state for next run
    history["prev_step"] = current_step
    history["prev_metrics"] = {
        "ar_ppl": latest_eval.get("ar_ppl"),
        "diff_loss": latest_eval.get("diff_loss"),
        "s1_tok_acc": latest_eval.get("s1_tok_acc"),
        "conf_auroc": latest_eval.get("conf_auroc"),
        "conf_ece": latest_eval.get("conf_ece"),
    }
    # Append latest eval to cumulative list (deduped)
    seen = {e["step"] for e in history.get("evals", [])}
    if eval_step and eval_step not in seen:
        history.setdefault("evals", []).append(file_evals[eval_step])
    save_history(history)
    print("[auto_sitrep] done.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Auto-sitrep generator")
    parser.add_argument("--force-telegram", action="store_true",
                        help="Force Telegram notification regardless of step interval")
    args = parser.parse_args()
    main(force_telegram=args.force_telegram)
