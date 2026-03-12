"""Generate a standalone HTML run report from training artifacts.

Reads eval metrics, benchmark results, compare_systems output, and cost ledger
from disk, then generates a single index.html matching the v2 report style.

Usage:
    python3 -m scripts.generate_run_report \
        --data-dir /opt/dlami/nvme/ml-lab \
        --config configs/tiny.yaml \
        --output-dir infra/reports/v3 \
        --run-version v3
"""

from __future__ import annotations

import argparse
import json
import glob
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import yaml


# v2 reference data for chart overlay comparison
V2_DATA = {
    "labels": ["1k", "5k", "10k", "20k", "30k", "40k", "50k"],
    "ar_ppl": [21.4, 25.6, 28.4, 30.9, 31.7, 30.2, 29.65],
    "diff_loss": [6.74, 4.97, 4.37, 4.75, 4.08, 4.56, 4.70],
    "s1_acc": [5.0, 18.0, 25.1, 21.3, 28.1, 23.2, 22.0],
    "auroc": [0.557, 0.824, 0.850, 0.851, 0.864, 0.857, 0.863],
}


def _normalize_eval(d: dict) -> dict:
    """Normalize eval metric field names to canonical short form."""
    mapping = {
        "ar_perplexity": "ar_ppl",
        "s1_token_accuracy": "s1_accuracy",
        "conf_auroc": "auroc",
        "conf_ece": "ece",
        "conf_accuracy": "conf_accuracy",
    }
    out = dict(d)
    for long_name, short_name in mapping.items():
        if long_name in out and short_name not in out:
            out[short_name] = out[long_name]
    # Convert s1_accuracy from fraction to percentage if needed
    if "s1_accuracy" in out and out["s1_accuracy"] < 1.0:
        out["s1_accuracy"] = round(out["s1_accuracy"] * 100, 1)
    return out


def load_eval_metrics(data_dir: str) -> list[dict]:
    """Load all eval_step_*.json files, sorted by step number."""
    pattern = os.path.join(data_dir, "eval_metrics", "**", "eval_step_*.json")
    files = glob.glob(pattern, recursive=True)
    evals = []
    for f in files:
        try:
            with open(f) as fh:
                d = json.load(fh)
                evals.append(_normalize_eval(d))
        except Exception:
            pass
    evals.sort(key=lambda x: x.get("step", 0))
    return evals


def load_benchmark_results(data_dir: str) -> dict | None:
    """Load the latest benchmark_step_*.json."""
    files = sorted(glob.glob(os.path.join(data_dir, "benchmarks", "benchmark_step_*.json")))
    if not files:
        return None
    try:
        with open(files[-1]) as f:
            return json.load(f)
    except Exception:
        return None


def load_compare_results(data_dir: str) -> dict | None:
    """Load the latest compare_step_*.json."""
    files = sorted(glob.glob(os.path.join(data_dir, "benchmarks", "compare_step_*.json")))
    if not files:
        return None
    try:
        with open(files[-1]) as f:
            return json.load(f)
    except Exception:
        return None


def load_cost_ledger(data_dir: str) -> dict | None:
    """Load cost_ledger.json."""
    path = os.path.join(data_dir, "cost", "cost_ledger.json")
    try:
        with open(path) as f:
            return json.load(f)
    except Exception:
        return None


def compute_targets(final_eval: dict) -> list[dict]:
    """Compute target achievement for the 5 key metrics."""
    targets = [
        {
            "label": "AR Perplexity",
            "key": "ar_ppl",
            "target_desc": "< 40",
            "target_val": 40.0,
            "lower_is_better": True,
        },
        {
            "label": "AUROC",
            "key": "auroc",
            "target_desc": "> 0.75",
            "target_val": 0.75,
            "lower_is_better": False,
        },
        {
            "label": "ECE",
            "key": "ece",
            "target_desc": "< 0.05",
            "target_val": 0.05,
            "lower_is_better": True,
        },
        {
            "label": "Diffusion Loss",
            "key": "diff_loss",
            "target_desc": "< 4.0",
            "target_val": 4.0,
            "lower_is_better": True,
        },
        {
            "label": "S1 Accuracy",
            "key": "s1_accuracy",
            "target_desc": "40%",
            "target_val": 40.0,
            "lower_is_better": False,
        },
    ]
    results = []
    for t in targets:
        val = final_eval.get(t["key"])
        if val is None:
            val = final_eval.get(t["key"].replace("_", " "), None)
        if val is None:
            results.append({**t, "value": "N/A", "status": "missed"})
            continue
        if t["lower_is_better"]:
            if val <= t["target_val"]:
                status = "met"
            elif val <= t["target_val"] * 1.2:
                status = "near"
            else:
                status = "missed"
        else:
            if val >= t["target_val"]:
                status = "met"
            elif val >= t["target_val"] * 0.8:
                status = "near"
            else:
                status = "missed"
        fmt = f"{val:.1%}" if t["key"] == "s1_accuracy" and val < 1.0 else f"{val}"
        if t["key"] == "s1_accuracy" and val > 1:
            fmt = f"{val:.1f}%"
        results.append({**t, "value": val, "formatted": fmt, "status": status})
    return results


def generate_html(
    run_version: str,
    config: dict,
    evals: list[dict],
    benchmarks: dict | None,
    compare: dict | None,
    cost_ledger: dict | None,
    targets: list[dict],
) -> str:
    """Generate standalone HTML report string."""
    now = datetime.now(timezone.utc)

    # Date range from cost ledger
    date_range = now.strftime("%B %Y")
    total_cost = 0.0
    num_sessions = 0
    if cost_ledger and "sessions" in cost_ledger:
        sessions = cost_ledger["sessions"]
        num_sessions = len(sessions)
        total_cost = sum(s.get("cost_usd", 0) for s in sessions)
        dates = []
        for s in sessions:
            for key in ("start_time", "started"):
                if key in s:
                    dates.append(s[key][:10])
                    break
        if dates:
            date_range = f"{dates[0]} to {dates[-1]}"

    final_step = evals[-1].get("step", 0) if evals else 0
    met_count = sum(1 for t in targets if t["status"] == "met")

    # Build eval table rows
    eval_rows = ""
    for e in evals:
        step = e.get("step", 0)
        is_final = (e == evals[-1]) if evals else False
        cls = ' class="highlight-row"' if is_final else ""
        s = "<strong>" if is_final else ""
        es = "</strong>" if is_final else ""
        eval_rows += f"""<tr{cls}>
          <td>{s}{step:,}{es}</td>
          <td class="num">{s}{e.get('ar_ppl', 'N/A')}{es}</td>
          <td class="num">{s}{e.get('diff_loss', 'N/A')}{es}</td>
          <td class="num">{s}{e.get('s1_accuracy', 'N/A')}%{es}</td>
          <td class="num">{s}{e.get('auroc', 'N/A')}{es}</td>
          <td class="num">{s}{e.get('ece', 'N/A')}{es}</td>
        </tr>"""

    # Target boxes
    target_html = ""
    status_colors = {"met": "green", "near": "yellow", "missed": "red"}
    for t in targets:
        color = status_colors.get(t["status"], "red")
        formatted = t.get("formatted", str(t.get("value", "N/A")))
        target_html += f"""<div class="target-box {t['status']}">
        <div class="t-label">{t['label']}</div>
        <div class="t-value {color}">{formatted}</div>
        <div class="t-target">Target: {t['target_desc']}</div>
        <span class="t-badge {t['status']}">{t['status'].title()}</span>
      </div>"""

    # Chart data from evals
    chart_labels = json.dumps([f"{e.get('step', 0) // 1000}k" for e in evals])
    chart_ar_ppl = json.dumps([e.get("ar_ppl", 0) for e in evals])
    chart_diff_loss = json.dumps([e.get("diff_loss", 0) for e in evals])
    chart_s1_acc = json.dumps([e.get("s1_accuracy", 0) for e in evals])
    chart_auroc = json.dumps([e.get("auroc", 0) for e in evals])

    # v2 comparison data
    v2_labels = json.dumps(V2_DATA["labels"])
    v2_ar_ppl = json.dumps(V2_DATA["ar_ppl"])
    v2_diff_loss = json.dumps(V2_DATA["diff_loss"])
    v2_s1_acc = json.dumps(V2_DATA["s1_acc"])
    v2_auroc = json.dumps(V2_DATA["auroc"])

    # Benchmark section
    benchmark_html = ""
    if benchmarks:
        benchmark_html = """<div class="card"><h2>Benchmark Results</h2><table>
        <thead><tr><th>Benchmark</th><th class="num">Metric</th><th class="num">Value</th></tr></thead><tbody>"""
        if "lambada" in benchmarks:
            lb = benchmarks["lambada"]
            acc = lb.get("accuracy", "N/A")
            acc_fmt = f"{acc:.1%}" if isinstance(acc, (int, float)) else acc
            benchmark_html += f'<tr><td>LAMBADA</td><td class="num">Accuracy</td><td class="num">{acc_fmt}</td></tr>'
            if "perplexity" in lb:
                benchmark_html += f'<tr><td>LAMBADA</td><td class="num">Perplexity</td><td class="num">{lb["perplexity"]:.2f}</td></tr>'
        if "wikitext" in benchmarks:
            wt = benchmarks["wikitext"]
            ppl = wt.get("perplexity", "N/A")
            ppl_fmt = f"{ppl:.2f}" if isinstance(ppl, (int, float)) else ppl
            benchmark_html += f'<tr><td>WikiText-103</td><td class="num">Perplexity</td><td class="num">{ppl_fmt}</td></tr>'
        benchmark_html += "</tbody></table></div>"

    # Compare systems section
    compare_html = ""
    if compare:
        compare_html = '<div class="card"><h2>System 1 vs System 2 Comparison</h2>'
        if "confidence" in compare:
            c = compare["confidence"]
            compare_html += f"""<div class="config-grid">
            <div class="config-item"><div class="c-label">ECE</div><div class="c-value">{c.get('ece', 'N/A')}</div></div>
            <div class="config-item"><div class="c-label">AUROC</div><div class="c-value">{c.get('auroc', 'N/A')}</div></div>
            <div class="config-item"><div class="c-label">Mean Confidence</div><div class="c-value">{c.get('mean_confidence', 'N/A')}</div></div>
            </div>"""
        if "quality" in compare:
            compare_html += '<table style="margin-top:16px"><thead><tr><th>System</th><th class="num">Perplexity</th></tr></thead><tbody>'
            for mode, ppl in compare["quality"].items():
                ppl_fmt = f"{ppl:.2f}" if isinstance(ppl, (int, float)) else ppl
                compare_html += f'<tr><td>{mode}</td><td class="num">{ppl_fmt}</td></tr>'
            compare_html += "</tbody></table>"
        if "escalation" in compare:
            compare_html += '<table style="margin-top:16px"><thead><tr><th>Threshold</th><th class="num">Escalation Rate (%)</th></tr></thead><tbody>'
            for thresh, rate in compare["escalation"].items():
                rate_fmt = f"{rate:.1f}" if isinstance(rate, (int, float)) else rate
                compare_html += f'<tr><td>{thresh}</td><td class="num">{rate_fmt}</td></tr>'
            compare_html += "</tbody></table>"
        compare_html += "</div>"

    # Cost table
    cost_html = ""
    if cost_ledger and "sessions" in cost_ledger:
        cost_html = '<div class="card"><h2>Spot Instance Cost History</h2><table><thead><tr><th>#</th><th>Type</th><th>AZ</th><th class="num">Cost</th><th>Finalized</th></tr></thead><tbody>'
        for i, s in enumerate(cost_ledger["sessions"], 1):
            inst_type = s.get("instance_type", "?")
            az = s.get("availability_zone", s.get("az", "?"))
            cost = s.get("cost_usd", 0)
            fin = "Yes" if s.get("finalized") else "No"
            fin_color = "var(--green)" if s.get("finalized") else "var(--yellow)"
            cost_html += f'<tr><td>{i}</td><td>{inst_type}</td><td>{az}</td><td class="num">${cost:.2f}</td><td style="color:{fin_color}">{fin}</td></tr>'
        cost_html += f'</tbody></table><div class="spot-total"><span class="label">Total ({num_sessions} sessions)</span><span class="value">${total_cost:.2f}</span></div></div>'

    # Config section
    model_name = config.get("model", {}).get("name", "GPT-2")
    total_steps = config.get("training", {}).get("max_steps", "?")
    precision = config.get("training", {}).get("precision", "bfloat16")
    lambda_ar = config.get("training", {}).get("lambda_ar", 1.0)
    lambda_diff = config.get("training", {}).get("lambda_diff", 1.0)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{run_version} Run Report &mdash; Dual-Process LM</title>
<link rel="icon" type="image/x-icon" href="/favicon.ico">
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
<style>
:root {{
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
  --purple: #a78bfa;
}}
*, *::before, *::after {{ margin: 0; padding: 0; box-sizing: border-box; }}
body {{
  font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
  background: var(--bg);
  color: var(--text);
  min-height: 100vh;
  padding: 32px 16px;
  line-height: 1.6;
}}
.container {{ max-width: 1000px; margin: 0 auto; }}
.header {{
  margin-bottom: 32px;
  padding: 60px 24px 20px;
  border-bottom: 1px solid var(--border);
  background: url('/hero.png') center -75px / cover no-repeat;
  position: relative;
  border-radius: 8px 8px 0 0;
}}
.header::before {{
  content: '';
  position: absolute;
  inset: 0;
  background: rgba(15, 17, 23, 0.65);
  border-radius: inherit;
}}
.header > * {{ position: relative; z-index: 1; }}
.header .breadcrumb {{ font-size: 13px; color: var(--dim); margin-bottom: 8px; }}
.header .breadcrumb a {{ color: var(--accent); text-decoration: none; }}
.header .breadcrumb a:hover {{ text-decoration: underline; }}
.header h1 {{ font-size: 24px; margin-bottom: 4px; }}
.header .subtitle {{ color: var(--dim); font-size: 14px; }}
.card {{
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 20px 24px;
  margin-bottom: 16px;
}}
.card h2 {{
  font-size: 14px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  color: var(--dim);
  margin-bottom: 16px;
}}
.targets-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 10px;
}}
.target-box {{
  background: var(--bg);
  border-radius: 6px;
  padding: 12px 14px;
  border-left: 3px solid transparent;
}}
.target-box.met {{ border-left-color: var(--green); }}
.target-box.missed {{ border-left-color: var(--red); }}
.target-box.near {{ border-left-color: var(--yellow); }}
.target-box .t-label {{ font-size: 11px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; }}
.target-box .t-value {{ font-size: 20px; font-weight: 700; margin: 4px 0 2px; }}
.target-box .t-value.green {{ color: var(--green); }}
.target-box .t-value.yellow {{ color: var(--yellow); }}
.target-box .t-value.red {{ color: var(--red); }}
.target-box .t-target {{ font-size: 12px; color: var(--dim); }}
.target-box .t-badge {{
  display: inline-block;
  font-size: 10px;
  font-weight: 700;
  padding: 1px 7px;
  border-radius: 8px;
  margin-top: 4px;
  text-transform: uppercase;
}}
.target-box .t-badge.met {{ background: var(--green); color: #000; }}
.target-box .t-badge.near {{ background: var(--yellow); color: #000; }}
.target-box .t-badge.missed {{ background: var(--red); color: #000; }}
.chart-row {{
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}}
@media (max-width: 700px) {{ .chart-row {{ grid-template-columns: 1fr; }} }}
.chart-box {{
  background: var(--bg);
  border-radius: 6px;
  padding: 16px;
  position: relative;
}}
.chart-box canvas {{ width: 100% !important; height: 220px !important; }}
table {{
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
}}
th {{
  text-align: left;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  color: var(--dim);
  padding: 8px 10px;
  border-bottom: 1px solid var(--border);
}}
td {{
  padding: 7px 10px;
  border-bottom: 1px solid rgba(42, 45, 58, 0.5);
}}
tr:hover td {{ background: rgba(96, 165, 250, 0.03); }}
.num {{ text-align: right; font-variant-numeric: tabular-nums; }}
.highlight-row td {{ background: rgba(96, 165, 250, 0.06); }}
.spot-total {{
  margin-top: 12px;
  padding-top: 10px;
  border-top: 1px solid var(--border);
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}}
.spot-total .label {{ color: var(--dim); }}
.spot-total .value {{ font-weight: 700; color: var(--accent); }}
.config-grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 10px;
}}
.config-item {{
  background: var(--bg);
  border-radius: 6px;
  padding: 10px 14px;
}}
.config-item .c-label {{ font-size: 11px; color: var(--dim); text-transform: uppercase; letter-spacing: 0.5px; }}
.config-item .c-value {{ font-size: 14px; font-weight: 600; margin-top: 2px; }}
.footer {{
  text-align: center;
  margin-top: 40px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  color: var(--dim);
  font-size: 12px;
}}
.footer a {{ color: var(--accent); text-decoration: none; }}
</style>
</head>
<body>
<div class="container">

  <div class="header">
    <div class="breadcrumb"><a href="../">Reports</a> / {run_version}</div>
    <h1>{run_version} &mdash; Dual-Process LM Run Report</h1>
    <div class="subtitle">{model_name} &middot; {final_step:,} steps &middot; {date_range} &middot; ${total_cost:.2f} total</div>
  </div>

  <!-- Target Achievement -->
  <div class="card">
    <h2>Target Achievement &mdash; {met_count} of {len(targets)} Met</h2>
    <div class="targets-grid">
      {target_html}
    </div>
  </div>

  <!-- Charts -->
  <div class="card">
    <h2>Training Trajectory ({run_version} vs v2)</h2>
    <div class="chart-row">
      <div class="chart-box"><canvas id="chart-loss"></canvas></div>
      <div class="chart-box"><canvas id="chart-confidence"></canvas></div>
    </div>
    <div class="chart-row" style="margin-top:16px">
      <div class="chart-box"><canvas id="chart-ppl"></canvas></div>
      <div class="chart-box"><canvas id="chart-s1acc"></canvas></div>
    </div>
  </div>

  <!-- Eval Table -->
  <div class="card">
    <h2>Evaluation Metrics by Step</h2>
    <div style="overflow-x:auto">
    <table>
      <thead>
        <tr>
          <th>Step</th>
          <th class="num">AR PPL</th>
          <th class="num">Diff Loss</th>
          <th class="num">S1 Acc</th>
          <th class="num">AUROC</th>
          <th class="num">ECE</th>
        </tr>
      </thead>
      <tbody>
        {eval_rows}
      </tbody>
    </table>
    </div>
  </div>

  {benchmark_html}
  {compare_html}
  {cost_html}

  <!-- Config -->
  <div class="card">
    <h2>Configuration</h2>
    <div class="config-grid">
      <div class="config-item"><div class="c-label">Model</div><div class="c-value">{model_name}</div></div>
      <div class="config-item"><div class="c-label">Total Steps</div><div class="c-value">{total_steps:,}</div></div>
      <div class="config-item"><div class="c-label">Precision</div><div class="c-value">{precision}</div></div>
      <div class="config-item"><div class="c-label">&lambda; AR / Diff</div><div class="c-value">{lambda_ar} / {lambda_diff}</div></div>
      <div class="config-item"><div class="c-label">Data</div><div class="c-value">OpenWebText</div></div>
      <div class="config-item"><div class="c-label">Total Cost</div><div class="c-value" style="color:var(--green)">${total_cost:.2f}</div></div>
    </div>
  </div>

  <div class="footer">
    Dual-Process LM &middot; bitbanshee research &middot;
    <a href="../">All Reports</a> &middot;
    <a href="https://train.bitbanshee.com">Dashboard</a> &middot;
    Generated {now.strftime("%Y-%m-%d %H:%M UTC")}
  </div>

</div>

<script>
const labels = {chart_labels};
const v3_arPPL = {chart_ar_ppl};
const v3_diffLoss = {chart_diff_loss};
const v3_s1Acc = {chart_s1_acc};
const v3_auroc = {chart_auroc};

const v2_labels = {v2_labels};
const v2_arPPL = {v2_ar_ppl};
const v2_diffLoss = {v2_diff_loss};
const v2_s1Acc = {v2_s1_acc};
const v2_auroc = {v2_auroc};

const baseOpts = {{
  responsive: true,
  maintainAspectRatio: false,
  interaction: {{ mode: 'index', intersect: false }},
  plugins: {{
    legend: {{ labels: {{ color: '#888', font: {{ size: 11, family: 'monospace' }} }} }},
    tooltip: {{ titleFont: {{ family: 'monospace' }}, bodyFont: {{ family: 'monospace' }} }}
  }},
  scales: {{
    x: {{ ticks: {{ color: '#555', font: {{ size: 10 }} }}, grid: {{ color: '#1f2233' }} }},
    y: {{ ticks: {{ color: '#555', font: {{ size: 10 }} }}, grid: {{ color: '#1f2233' }} }}
  }}
}};

function mkOpts(overrides) {{
  return JSON.parse(JSON.stringify({{ ...baseOpts, ...overrides }}));
}}

function v2Style(label) {{
  return {{
    label: label,
    borderColor: 'rgba(136,136,136,0.4)',
    borderWidth: 1,
    borderDash: [5, 5],
    pointRadius: 2,
    pointBackgroundColor: '#555',
    tension: 0.3,
    fill: false
  }};
}}

// Chart 1: Diffusion Loss
new Chart(document.getElementById('chart-loss'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{
        label: '{run_version} Diff Loss',
        data: v3_diffLoss,
        borderColor: '#fb923c',
        backgroundColor: 'rgba(251,146,60,0.1)',
        fill: true,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#fb923c',
        tension: 0.3
      }},
      {{ ...v2Style('v2 Diff Loss'), data: v2_diffLoss, labels: v2_labels }}
    ]
  }},
  options: (() => {{
    const o = mkOpts({{}});
    o.plugins.title = {{ display: true, text: 'Diffusion Loss', color: '#888', font: {{ size: 13, family: 'monospace' }} }};
    return o;
  }})()
}});

// Chart 2: S1 Accuracy + AUROC
new Chart(document.getElementById('chart-confidence'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{
        label: '{run_version} AUROC',
        data: v3_auroc,
        borderColor: '#a78bfa',
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#a78bfa',
        tension: 0.3,
        yAxisID: 'y'
      }},
      {{ ...v2Style('v2 AUROC'), data: v2_auroc, yAxisID: 'y' }}
    ]
  }},
  options: (() => {{
    const o = mkOpts({{}});
    o.plugins.title = {{ display: true, text: 'AUROC', color: '#888', font: {{ size: 13, family: 'monospace' }} }};
    return o;
  }})()
}});

// Chart 3: AR PPL
new Chart(document.getElementById('chart-ppl'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{
        label: '{run_version} AR PPL',
        data: v3_arPPL,
        borderColor: '#f87171',
        backgroundColor: 'rgba(248,113,113,0.1)',
        fill: true,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#f87171',
        tension: 0.3
      }},
      {{ ...v2Style('v2 AR PPL'), data: v2_arPPL, labels: v2_labels }}
    ]
  }},
  options: (() => {{
    const o = mkOpts({{}});
    o.plugins.title = {{ display: true, text: 'AR Perplexity', color: '#888', font: {{ size: 13, family: 'monospace' }} }};
    return o;
  }})()
}});

// Chart 4: S1 Accuracy
new Chart(document.getElementById('chart-s1acc'), {{
  type: 'line',
  data: {{
    labels,
    datasets: [
      {{
        label: '{run_version} S1 Acc (%)',
        data: v3_s1Acc,
        borderColor: '#34d399',
        backgroundColor: 'rgba(52,211,153,0.1)',
        fill: true,
        borderWidth: 2,
        pointRadius: 4,
        pointBackgroundColor: '#34d399',
        tension: 0.3
      }},
      {{ ...v2Style('v2 S1 Acc (%)'), data: v2_s1Acc, labels: v2_labels }}
    ]
  }},
  options: (() => {{
    const o = mkOpts({{}});
    o.plugins.title = {{ display: true, text: 'S1 Accuracy (%)', color: '#888', font: {{ size: 13, family: 'monospace' }} }};
    return o;
  }})()
}});
</script>
</body>
</html>"""
    return html


def main() -> None:
    """CLI entry point: generate HTML report from training artifacts."""
    parser = argparse.ArgumentParser(description="Generate run report HTML")
    parser.add_argument("--data-dir", type=str, required=True, help="Path to data directory")
    parser.add_argument("--config", type=str, required=True, help="Path to YAML config")
    parser.add_argument("--output-dir", type=str, required=True, help="Output directory for report")
    parser.add_argument("--run-version", type=str, default="v3", help="Run version label")
    args = parser.parse_args()

    with open(args.config) as f:
        config = yaml.safe_load(f)

    evals = load_eval_metrics(args.data_dir)
    benchmarks = load_benchmark_results(args.data_dir)
    compare = load_compare_results(args.data_dir)
    cost_ledger = load_cost_ledger(args.data_dir)

    if not evals:
        print("WARNING: No eval metrics found. Report will be minimal.")

    final_eval = evals[-1] if evals else {}
    targets = compute_targets(final_eval)

    html = generate_html(
        run_version=args.run_version,
        config=config,
        evals=evals,
        benchmarks=benchmarks,
        compare=compare,
        cost_ledger=cost_ledger,
        targets=targets,
    )

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "index.html"
    output_path.write_text(html)
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
