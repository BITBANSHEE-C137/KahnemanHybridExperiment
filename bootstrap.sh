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
sudo mkdir -p "$DATA_DIR"/{hf_cache,checkpoints}
sudo chown -R ubuntu:ubuntu "$DATA_DIR"

# ── Pull operational files from S3 ──
echo "Pulling operational files from S3..."
aws s3 cp "s3://$S3_BUCKET/deploy/dashboard.py" "$PROJECT/dashboard.py" --region "$REGION"
aws s3 cp "s3://$S3_BUCKET/deploy/STATUS.md" "$PROJECT/STATUS.md" --region "$REGION" || true

# ── Ubuntu user environment ──
echo "Configuring ubuntu user environment..."
sudo -u ubuntu bash -c "
  # Clean old env vars
  sed -i '/GH_TOKEN/d; /CLAUDE_CODE_OAUTH_TOKEN/d; /HF_HOME/d; /CHECKPOINT_DIR/d' ~/.bashrc

  # Inject env vars
  echo 'export GH_TOKEN=\"$GH_TOKEN\"' >> ~/.bashrc
  echo 'export HF_HOME=$DATA_DIR/hf_cache' >> ~/.bashrc
  echo 'export CHECKPOINT_DIR=$DATA_DIR/checkpoints' >> ~/.bashrc

  # Git credentials
  echo 'https://x-access-token:$GH_TOKEN@github.com' > ~/.git-credentials
  git config --global credential.helper store

  # Pull latest code
  cd $PROJECT
  git pull --ff-only || true
"

# ── Pull and start checkpoint sync ──
echo "Setting up checkpoint sync to S3..."
aws s3 cp "s3://$S3_BUCKET/deploy/sync-checkpoints.sh" "$PROJECT/sync-checkpoints.sh" --region "$REGION"
chmod +x "$PROJECT/sync-checkpoints.sh"
sudo -u ubuntu bash -c "nohup $PROJECT/sync-checkpoints.sh >> /var/log/checkpoint-sync.log 2>&1 &"

# ── Start tmux session ──
echo "Starting tmux session..."
sudo -u ubuntu setsid tmux new-session -d -s training -c "$PROJECT"

echo "=== Bootstrap.sh completed at $(date -u) ==="
echo "Dashboard: python3 dashboard.py"
