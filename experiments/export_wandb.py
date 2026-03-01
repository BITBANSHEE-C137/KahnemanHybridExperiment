#!/usr/bin/env python3
"""Export full training history from Weights & Biases.

Usage:
    pip install wandb
    wandb login
    python experiments/export_wandb.py

Exports all logged metrics to experiments/wandb_full_history.csv.
"""

import csv
import wandb

ENTITY = "bitbanshee-c137"
PROJECT = "dual-process-lm"

api = wandb.Api()
runs = api.runs(f"{ENTITY}/{PROJECT}")

print(f"Found {len(runs)} runs in {ENTITY}/{PROJECT}")

all_rows = []
for run in runs:
    print(f"  Exporting run: {run.name} ({run.id}, {run.state})")
    history = run.scan_history()
    for row in history:
        row["run_id"] = run.id
        row["run_name"] = run.name
        all_rows.append(row)

if not all_rows:
    print("No data found.")
    exit(1)

# Collect all unique keys
all_keys = set()
for row in all_rows:
    all_keys.update(row.keys())

# Sort keys: run metadata first, then _step, then alphabetical
meta = ["run_id", "run_name", "_step", "_runtime", "_timestamp"]
other = sorted(all_keys - set(meta))
fieldnames = [k for k in meta if k in all_keys] + other

out_path = "experiments/wandb_full_history.csv"
with open(out_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(all_rows)

print(f"Wrote {len(all_rows)} rows to {out_path}")
