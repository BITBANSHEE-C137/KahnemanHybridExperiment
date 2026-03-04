#!/bin/bash
set -uo pipefail
S3_BUCKET="${S3_BUCKET:-ml-lab-004507070771/dual-system-research-data}"
DATA_DIR="${DATA_DIR:-/opt/dlami/nvme/ml-lab}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
CHECKPOINT_S3_PREFIX="${CHECKPOINT_S3_PREFIX:-checkpoints}"
EVAL_S3_PREFIX="${EVAL_S3_PREFIX:-eval_metrics}"
INTERVAL=60

echo "[sync] Artifact sync daemon started at $(date -u)"

sync_all() {
    for subdir in checkpoints eval_metrics benchmarks logs preprocessed cost; do
        local_dir="$DATA_DIR/$subdir"
        case "$subdir" in
            checkpoints)  s3_dest="$CHECKPOINT_S3_PREFIX" ;;
            eval_metrics) s3_dest="$EVAL_S3_PREFIX" ;;
            *)            s3_dest="$subdir" ;;
        esac
        if [ -d "$local_dir" ] && [ "$(ls -A "$local_dir" 2>/dev/null)" ]; then
            aws s3 sync "$local_dir/" "s3://$S3_BUCKET/$s3_dest/" --region "$REGION" 2>&1 | \
                while read -r line; do echo "[sync][$subdir] $line"; done
        fi
    done

    # sync wandb/ from project directory (not in DATA_DIR)
    local wandb_dir="/home/ubuntu/KahnemanHybridExperiment/wandb"
    if [ -d "$wandb_dir" ] && [ "$(ls -A "$wandb_dir" 2>/dev/null)" ]; then
        aws s3 sync "$wandb_dir/" "s3://$S3_BUCKET/wandb/" --region "$REGION" --no-follow-symlinks 2>&1 | \
            while read -r line; do echo "[sync][wandb] $line"; done
    fi

    # sync sitrep.md from project directory
    local sitrep_file="/home/ubuntu/KahnemanHybridExperiment/sitrep.md"
    if [ -f "$sitrep_file" ]; then
        aws s3 cp "$sitrep_file" "s3://$S3_BUCKET/sitrep.md" --region "$REGION" 2>&1 | \
            while read -r line; do echo "[sync][sitrep] $line"; done
    fi
}

cleanup() {
    echo "[sync] SIGTERM — final sync..."
    sync_all
    export_csvs
    export_training_history
    echo "[sync] Final sync complete."
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
        git commit -m "Update experiment CSVs (auto-export at step $(ls "$eval_dir"/eval_step_*.json | sort -t_ -k3 -n | tail -1 | grep -oP '\d+(?=\.json)'))" --no-gpg-sign 2>&1 | \
            while read -r line; do echo "[sync][csv] $line"; done
        git push 2>&1 | while read -r line; do echo "[sync][csv] $line"; done
    fi
}

export_training_history() {
    local project_dir="/home/ubuntu/KahnemanHybridExperiment"

    # Collect all log files (same sources as export_csvs)
    local log_files
    log_files=$(ls "$project_dir"/wandb/run-*/files/output.log "$DATA_DIR"/logs/full_run.log 2>/dev/null)
    [ -n "$log_files" ] || return 0

    # Count total lines across all logs — only re-export if new data appeared
    local current_step_count
    current_step_count=$(grep -c 'step:' $log_files 2>/dev/null | awk -F: '{s+=$NF} END {print s+0}')
    if [ "$current_step_count" = "${_last_step_count:-0}" ]; then
        return 0
    fi
    _last_step_count="$current_step_count"

    echo "[sync][history] Exporting training_history.json ($current_step_count step lines)..."

    python3 -c "
import json, glob, os, re

project = '$project_dir'
data_dir = '$DATA_DIR'

pat = re.compile(
    r'step:\s*(\d+)\s*\|'
    r'\s*ar_loss:\s*([\d.]+)\s*\|'
    r'\s*diff_loss:\s*([\d.]+)\s*\|'
    r'\s*conf_acc:\s*([\d.]+)\s*\|'
    r'\s*lr:\s*([\d.eE+-]+)\s*\|'
    r'\s*time:\s*([\d.]+)s'
)

steps = {}
logs = glob.glob(os.path.join(project, 'wandb/run-*/files/output.log'))
logs += glob.glob(os.path.join(data_dir, 'logs/full_run.log'))
for lf in logs:
    with open(lf) as fh:
        for line in fh:
            m = pat.search(line)
            if m:
                s = int(m.group(1))
                steps[s] = {
                    'step': s,
                    'ar_loss': float(m.group(2)),
                    'diff_loss': float(m.group(3)),
                    'conf_acc': float(m.group(4)),
                    'lr': float(m.group(5)),
                    'elapsed_s': float(m.group(6)),
                }

history = sorted(steps.values(), key=lambda x: x['step'])
out_path = os.path.join(data_dir, 'training_history.json')
os.makedirs(os.path.dirname(out_path), exist_ok=True)
with open(out_path, 'w') as f:
    json.dump(history, f)

print(f'[sync][history] Wrote {len(history)} steps to {out_path}')
" 2>&1

    # Upload to S3
    local history_file="$DATA_DIR/training_history.json"
    if [ -f "$history_file" ]; then
        aws s3 cp "$history_file" "s3://$S3_BUCKET/training_history.json" --region "$REGION" 2>&1 | \
            while read -r line; do echo "[sync][history] $line"; done
    fi
}

while true; do
    sync_all
    export_csvs
    export_training_history
    for i in $(seq 1 $INTERVAL); do sleep 1; done
done
