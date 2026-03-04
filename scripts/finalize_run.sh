#!/usr/bin/env bash
# finalize_run.sh — Post-training finalization for v2.
# Runs benchmarks, updates sitrep, prints fleet shutdown command.
# Does NOT auto-execute shutdown.
set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/KahnemanHybridExperiment}"
DATA_DIR="${DATA_DIR:-/opt/dlami/nvme/ml-lab}"
S3_BUCKET="${S3_BUCKET:-ml-lab-004507070771/dual-system-research-data}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
FLEET_ID="fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"

echo "=== V2 Run Finalization ==="
echo "Started: $(date -u)"
echo ""

# 1. Find latest checkpoint
LATEST_CKPT=$(ls -t "$DATA_DIR/checkpoints/v2/"step_*.pt 2>/dev/null | head -1)
if [ -z "$LATEST_CKPT" ]; then
    echo "ERROR: No v2 checkpoints found in $DATA_DIR/checkpoints/v2/"
    exit 1
fi
echo "Latest checkpoint: $LATEST_CKPT"

# 2. Run benchmarks
echo ""
echo "--- Running LAMBADA + WikiText-103 benchmarks ---"
cd "$PROJECT_DIR"
python3 -m scripts.benchmark --checkpoint "$LATEST_CKPT" --config configs/tiny.yaml || echo "WARNING: Benchmarks failed"

# 3. Run confidence analysis
echo ""
echo "--- Running confidence analysis ---"
python3 -m scripts.compare_systems --checkpoint "$LATEST_CKPT" --config configs/tiny.yaml || echo "WARNING: Confidence analysis failed"

# 4. Finalize cost tracker
echo ""
echo "--- Finalizing cost tracker ---"
bash cost-tracker.sh finalize || echo "WARNING: Cost tracker finalize failed"

# 5. Update sitrep
echo ""
echo "--- Updating sitrep ---"
python3 auto_sitrep.py || echo "WARNING: Auto-sitrep failed"

# 6. Sync all artifacts to S3
echo ""
echo "--- Final S3 sync ---"
aws s3 sync "$DATA_DIR/checkpoints/v2/" "s3://$S3_BUCKET/checkpoints/v2/" --region "$REGION" || true
aws s3 sync "$DATA_DIR/eval_metrics/" "s3://$S3_BUCKET/eval_metrics/" --region "$REGION" || true
aws s3 sync "$DATA_DIR/benchmarks/" "s3://$S3_BUCKET/benchmarks/" --region "$REGION" || true
aws s3 sync "$DATA_DIR/logs/" "s3://$S3_BUCKET/logs/" --region "$REGION" || true

echo ""
echo "=== Finalization complete ==="
echo ""
echo "To shut down the fleet (set capacity to 0):"
echo "  aws ec2 modify-fleet --fleet-id $FLEET_ID --target-capacity-specification TotalTargetCapacity=0,SpotTargetCapacity=0 --region $REGION"
echo ""
echo "WARNING: 'maintain' type auto-replaces terminated instances."
echo "Always set capacity to 0 BEFORE terminating instances."
