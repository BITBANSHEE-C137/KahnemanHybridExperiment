#!/bin/bash
set -uo pipefail
S3_BUCKET="${S3_BUCKET:-ml-lab-004507070771/dual-system-research-data}"
DATA_DIR="${DATA_DIR:-/opt/dlami/nvme/ml-lab}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
INTERVAL=60

echo "[sync] Artifact sync daemon started at $(date -u)"

sync_all() {
    for subdir in checkpoints eval_metrics benchmarks logs preprocessed cost; do
        local_dir="$DATA_DIR/$subdir"
        if [ -d "$local_dir" ] && [ "$(ls -A "$local_dir" 2>/dev/null)" ]; then
            aws s3 sync "$local_dir/" "s3://$S3_BUCKET/$subdir/" --region "$REGION" 2>&1 | \
                while read -r line; do echo "[sync][$subdir] $line"; done
        fi
    done
}

cleanup() {
    echo "[sync] SIGTERM — final sync..."
    sync_all
    exit 0
}
trap cleanup SIGTERM SIGINT

export_csvs() {
    local project_dir="/home/ubuntu/KahnemanHybridExperiment"
    local eval_dir="$DATA_DIR/eval_metrics"
    local experiments_dir="$project_dir/experiments"

    # Skip if no eval data yet
    [ -d "$eval_dir" ] && [ "$(ls "$eval_dir"/eval_step_*.json 2>/dev/null)" ] || return 0

    # Count eval JSONs — only re-export if new checkpoints appeared
    local current_count
    current_count=$(ls "$eval_dir"/eval_step_*.json 2>/dev/null | wc -l)
    if [ "$current_count" = "${_last_eval_count:-0}" ]; then
        return 0
    fi
    _last_eval_count="$current_count"

    echo "[sync][csv] Exporting experiment CSVs ($current_count eval checkpoints)..."

    python3 -c "
import csv, json, glob, os, re

project = '$project_dir'
data_dir = '$DATA_DIR'
exp_dir = os.path.join(project, 'experiments')
os.makedirs(exp_dir, exist_ok=True)

# --- eval_metrics.csv ---
rows = []
for f in sorted(glob.glob(os.path.join(data_dir, 'eval_metrics/eval_step_*.json'))):
    with open(f) as fh:
        rows.append(json.load(fh))
rows.sort(key=lambda x: x['step'])
fields = ['step','ar_perplexity','diff_loss','s1_token_accuracy','conf_accuracy','conf_ece','conf_auroc']
with open(os.path.join(exp_dir, 'eval_metrics.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
    w.writeheader()
    w.writerows(rows)

# --- training_steps.csv ---
pat = re.compile(r'step:\s*(\d+)\s*\|\s*ar_loss:\s*([\d.]+)\s*\|\s*diff_loss:\s*([\d.]+)\s*\|\s*conf_acc:\s*([\d.]+)\s*\|\s*lr:\s*([\d.eE+-]+)')
steps = {}
logs = glob.glob(os.path.join(project, 'wandb/run-*/files/output.log'))
logs += glob.glob(os.path.join(data_dir, 'logs/full_run.log'))
for lf in logs:
    with open(lf) as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                s = int(m.group(1))
                steps[s] = {'step':s, 'ar_loss':float(m.group(2)), 'diff_loss':float(m.group(3)),
                             'conf_accuracy':float(m.group(4)), 'learning_rate':float(m.group(5))}
sfields = ['step','ar_loss','diff_loss','conf_accuracy','learning_rate']
with open(os.path.join(exp_dir, 'training_steps.csv'), 'w', newline='') as f:
    w = csv.DictWriter(f, fieldnames=sfields)
    w.writeheader()
    w.writerows(sorted(steps.values(), key=lambda x: x['step']))

print(f'[sync][csv] Wrote {len(rows)} eval rows, {len(steps)} training rows')
" 2>&1

    # Auto-commit if CSVs changed
    cd "$project_dir" || return 1
    if ! git diff --quiet experiments/ 2>/dev/null; then
        git add experiments/eval_metrics.csv experiments/training_steps.csv
        git commit -m "Update experiment CSVs (auto-export at step $(ls "$eval_dir"/eval_step_*.json | sort -t_ -k3 -n | tail -1 | grep -oP '\d+(?=\.json)'))" --no-gpg-sign 2>&1 |             while read -r line; do echo "[sync][csv] $line"; done
        git push 2>&1 | while read -r line; do echo "[sync][csv] $line"; done
    fi
}

while true; do
    sync_all
    export_csvs
    for i in $(seq 1 $INTERVAL); do sleep 1; done
done
