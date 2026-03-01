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

while true; do
    sync_all
    for i in $(seq 1 $INTERVAL); do sleep 1; done
done
