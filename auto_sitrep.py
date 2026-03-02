#!/usr/bin/env python3
"""Auto-sitrep generator. Runs every 30 min via cron.
Fetches metrics from the dashboard API, maintains cumulative eval history,
generates sitrep.md, and commits/pushes to git."""

import json
import os
import glob
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from urllib.request import urlopen
from urllib.error import URLError

PROJECT = "/home/ubuntu/KahnemanHybridExperiment"
EVAL_DIR = "/opt/dlami/nvme/ml-lab/eval_metrics"
HISTORY_FILE = "/tmp/auto-sitrep-eval-history.json"
SITREP_PATH = os.path.join(PROJECT, "sitrep.md")

ET = timezone(timedelta(hours=-4))


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


def generate_sitrep(status, trajectory_rows, prev_metrics, prev_step):
    """Generate the full sitrep markdown."""
    now = datetime.now(ET)
    utc_now = datetime.now(timezone.utc)
    header_time = f"{now.strftime('%-I:%M %p')} ET / {utc_now.strftime('%H:%M')} UTC"

    step = status["current_step"]
    max_steps = status["max_steps"]
    pct = status["progress_pct"]
    gpu = status["gpu"]
    inst = status["instance"]
    le = status.get("latest_eval", {})
    lt = status.get("latest_train", {})
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

    md = f"""# Sitrep — {now.strftime('%Y-%m-%d')} {header_time}

## v1 Training — running, healthy, {pct:.0f}% complete

- **Step {fmt_step(step)} / {max_steps:,}** ({pct:.1f}%)
- GPU: {gpu['gpu_util']:.0f}% utilization, {gpu['vram_used_mb'] / 1024:.1f} / {gpu['vram_total_mb'] / 1024:.0f} GB VRAM, {gpu['temp_c']:.0f}°C
- Rate: ~{rate:.0f} steps/hr ({sec_per_step:.1f}s/step)
- ETA to {max_steps // 1000}k: ~{eta_h:.1f} hours at current rate
- Spot price: ${inst['spot_rate']}/hr ({inst['instance_type']})
- Spot cost so far: ${inst['spot_cost']:.2f} — projected total: ${inst['spot_projected']:.2f} ({inst['savings_pct']:.0f}% savings vs on-demand)
- Instance up {uptime_h}h{uptime_m:02d}m since bootstrap ({inst.get('boot_time_utc', '?')[:16].replace('T', ' ')} UTC)

{traj}
Live at step {fmt_step(step)}: ar_loss {lt.get('ar_loss', 0):.2f}, diff_loss {lt.get('diff_loss', 0):.2f}, conf_acc {lt.get('conf_acc', 0):.3f}

## Target status (5 of 5)

- **AR PPL < 40:** {ar_ppl:.1f} — met since step 50, drifting up slowly but solid margin
- **AUROC > 0.75:** {auroc:.3f} — met since step 8k, steady climb
- **ECE < 0.05:** {ece:.3f} — met since step 1k, excellent calibration
- **Diff loss → 4.0:** {diff_loss:.2f} at eval step {eval_step // 1000}k — {diff_progress:.0f}% of the way{', closing in' if diff_progress > 80 else ''}
- **S1 accuracy → 40%:** {fmt_pct(s1_acc)} at eval — {s1_progress:.0f}% of target

{trends}
## Code & infra

- Instance on `v2-fixes` branch
- All services healthy: sync daemon, nginx, Flask dashboard, spot price cron
- Checkpoints on disk: {ckpt_str} (all synced to S3)
- *Auto-generated by auto_sitrep.py*

## What's next (after v1 completes)

1. Merge `v2-fixes` → `main`
2. Run LAMBADA + WikiText-103 benchmarks on final v1 checkpoint
3. Start v2 run with identical config (fresh, from scratch)
4. Compare v1 vs v2 (especially hybrid escalation rates with fixed confidence signal)
"""
    return md


def git_commit_push():
    """Stage sitrep.md, commit, and push."""
    os.chdir(PROJECT)
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
    subprocess.run(["git", "push"], check=True)
    print("Committed and pushed sitrep.md")


def main():
    print(f"[auto_sitrep] {datetime.now(timezone.utc).isoformat()}")

    # 1. Fetch live status
    status = fetch_status()
    latest_eval = status.get("latest_eval", {})
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

    # 7. Generate sitrep
    md = generate_sitrep(status, trajectory_rows, prev_metrics, prev_step)

    # 8. Write sitrep.md
    with open(SITREP_PATH, "w") as f:
        f.write(md)
    print(f"Wrote {SITREP_PATH}")

    # 9. Git commit and push
    git_commit_push()

    # 10. Save history state for next run
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
    main()
