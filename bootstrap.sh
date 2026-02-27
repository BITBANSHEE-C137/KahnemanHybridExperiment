#!/bin/bash
set -euo pipefail
GH_TOKEN="$1"
REGION="us-east-1"
S3_BUCKET="ml-lab-004507070771/dual-system-research-data"
PROJECT="/home/ubuntu/KahnemanHybridExperiment"
NVME="/opt/dlami/nvme"
DATA_DIR="$NVME/ml-lab"

echo "=== Bootstrap.sh started at $(date -u) ==="

# ── Ephemeral NVMe setup ──
echo "Setting up ephemeral NVMe at $DATA_DIR..."
sudo mkdir -p "$DATA_DIR"/{hf_cache,checkpoints,logs,benchmarks,eval_metrics,preprocessed}
sudo chown -R ubuntu:ubuntu "$DATA_DIR"

# ── Fetch W&B API key from Secrets Manager ──
echo "Fetching W&B API key from Secrets Manager..."
WANDB_API_KEY=$(aws secretsmanager get-secret-value --secret-id "ml-lab/wandb-api-key" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")

# ── Ubuntu user environment ──
echo "Configuring ubuntu user environment..."
sudo -u ubuntu bash << ENVBLOCK
  # Clean old env vars
  sed -i '/GH_TOKEN/d; /CLAUDE_CODE_OAUTH_TOKEN/d; /HF_HOME/d; /CHECKPOINT_DIR/d; /WANDB_API_KEY/d; /S3_BUCKET/d; /DATA_DIR/d; /AWS_DEFAULT_REGION/d; /PREPROCESSED_DATA_DIR/d' ~/.bashrc

  # Inject env vars
  echo 'export GH_TOKEN="$GH_TOKEN"' >> ~/.bashrc
  echo 'export HF_HOME=$DATA_DIR/hf_cache' >> ~/.bashrc
  echo 'export CHECKPOINT_DIR=$DATA_DIR/checkpoints' >> ~/.bashrc
  echo 'export WANDB_API_KEY="$WANDB_API_KEY"' >> ~/.bashrc
  echo 'export S3_BUCKET="$S3_BUCKET"' >> ~/.bashrc
  echo 'export DATA_DIR="$DATA_DIR"' >> ~/.bashrc
  echo 'export AWS_DEFAULT_REGION="$REGION"' >> ~/.bashrc
  echo 'export PREPROCESSED_DATA_DIR="$DATA_DIR/preprocessed"' >> ~/.bashrc

  # Git credentials
  echo 'https://x-access-token:$GH_TOKEN@github.com' > ~/.git-credentials
  git config --global credential.helper store

  # Pull latest code — clean tree first to avoid merge conflicts
  cd $PROJECT
  git checkout -- . && git clean -fd
  git pull --ff-only || true
ENVBLOCK

# ── Pull operational files from S3 (AFTER git pull to avoid conflicts) ──
echo "Pulling operational files from S3..."
aws s3 cp "s3://$S3_BUCKET/deploy/dashboard.py" "$PROJECT/dashboard.py" --region "$REGION" || true
aws s3 cp "s3://$S3_BUCKET/deploy/STATUS.md" "$PROJECT/STATUS.md" --region "$REGION" || true

# ── Restore prior artifacts from S3 (for training resume) ──
echo "Restoring prior artifacts from S3..."
aws s3 sync "s3://$S3_BUCKET/checkpoints/" "$DATA_DIR/checkpoints/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/logs/" "$DATA_DIR/logs/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/eval_metrics/" "$DATA_DIR/eval_metrics/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/benchmarks/" "$DATA_DIR/benchmarks/" --region "$REGION" || true
echo "Restored artifacts:"
ls -la "$DATA_DIR/checkpoints/" 2>/dev/null || echo "  (no checkpoints)"

# ── Sync pre-processed training data from S3 ──
echo "Syncing pre-processed data from S3..."
aws s3 sync "s3://$S3_BUCKET/preprocessed/" "$DATA_DIR/preprocessed/" --region "$REGION" || true
echo "Pre-processed data:"
ls -lh "$DATA_DIR/preprocessed/" 2>/dev/null || echo "  (no preprocessed data)"

# ── Pull and start artifact sync daemon ──
echo "Setting up artifact sync to S3..."
aws s3 cp "s3://$S3_BUCKET/deploy/sync-checkpoints.sh" "$PROJECT/sync-checkpoints.sh" --region "$REGION"
chmod +x "$PROJECT/sync-checkpoints.sh"
sudo -u ubuntu bash -c "S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' nohup $PROJECT/sync-checkpoints.sh >> /var/log/artifact-sync.log 2>&1 &"

# ── Start tmux session ──
echo "Starting tmux session..."
sudo -u ubuntu setsid tmux new-session -d -s training -c "$PROJECT"

echo "=== Bootstrap.sh completed at $(date -u) ==="
echo "Dashboard: python3 dashboard.py"
