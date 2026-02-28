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

# ── Fetch secrets from Secrets Manager ──
echo "Fetching secrets from Secrets Manager..."
WANDB_API_KEY=$(aws secretsmanager get-secret-value --secret-id "ml-lab/wandb-api-key" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
HF_TOKEN=$(aws secretsmanager get-secret-value --secret-id "ml-lab/hf-token" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
SPOT_TOKEN=$(aws secretsmanager get-secret-value --secret-id "ml-lab/dashboard-spot-token" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")

# ── Ubuntu user environment ──
echo "Configuring ubuntu user environment..."
# Clean old env vars
sudo -u ubuntu sed -i '/GH_TOKEN/d; /CLAUDE_CODE_OAUTH_TOKEN/d; /HF_HOME/d; /CHECKPOINT_DIR/d; /WANDB_API_KEY/d; /HF_TOKEN/d; /HUGGING_FACE_HUB_TOKEN/d; /S3_BUCKET/d; /DATA_DIR/d; /AWS_DEFAULT_REGION/d; /PREPROCESSED_DATA_DIR/d; /SPOT_TOKEN/d; /PYTORCH_CUDA_ALLOC_CONF/d' /home/ubuntu/.bashrc

# Inject env vars
cat >> /home/ubuntu/.bashrc << BASHRC
export GH_TOKEN="$GH_TOKEN"
export HF_HOME=$DATA_DIR/hf_cache
export CHECKPOINT_DIR=$DATA_DIR/checkpoints
export WANDB_API_KEY="$WANDB_API_KEY"
export HF_TOKEN="$HF_TOKEN"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
export S3_BUCKET="$S3_BUCKET"
export DATA_DIR="$DATA_DIR"
export AWS_DEFAULT_REGION="$REGION"
export PREPROCESSED_DATA_DIR="$DATA_DIR/preprocessed"
export SPOT_TOKEN="$SPOT_TOKEN"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
BASHRC

# Git credentials
sudo -u ubuntu bash -c "echo 'https://x-access-token:$GH_TOKEN@github.com' > ~/.git-credentials && git config --global credential.helper store"

# Pull latest code
sudo -u ubuntu bash -c "cd $PROJECT && git checkout -- . && git clean -fd && git pull --ff-only" || true

# ── Restore prior artifacts from S3 ──
echo "Restoring prior artifacts from S3..."
aws s3 sync "s3://$S3_BUCKET/checkpoints/" "$DATA_DIR/checkpoints/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/logs/" "$DATA_DIR/logs/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/eval_metrics/" "$DATA_DIR/eval_metrics/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/benchmarks/" "$DATA_DIR/benchmarks/" --region "$REGION" || true
echo "Restored checkpoints:"
ls -lh "$DATA_DIR/checkpoints/"*.pt 2>/dev/null || echo "  (none)"

# ── Sync pre-processed training data from S3 ──
echo "Syncing pre-processed data from S3..."
aws s3 sync "s3://$S3_BUCKET/preprocessed/" "$DATA_DIR/preprocessed/" --region "$REGION" || true
ls -lh "$DATA_DIR/preprocessed/" 2>/dev/null

# ── Fix ownership (S3 restores as root) ──
sudo chown -R ubuntu:ubuntu "$DATA_DIR"

# ── 1. DNS update ──
echo "Updating DNS..."
sudo -u ubuntu bash "$PROJECT/update-dns.sh" || echo "WARNING: DNS update failed (non-fatal)"

# ── 2. Start artifact sync daemon ──
echo "Starting sync daemon..."
sudo touch /var/log/artifact-sync.log
sudo chown ubuntu:ubuntu /var/log/artifact-sync.log
sudo -u ubuntu bash -c "cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' nohup bash sync-checkpoints.sh >> /var/log/artifact-sync.log 2>&1 &"
sleep 1
pgrep -f sync-checkpoints.sh > /dev/null && echo "  sync daemon: RUNNING" || echo "  WARNING: sync daemon failed to start"

# ── 3. Install nginx + certbot if missing ──
echo "Setting up nginx + TLS..."
if ! command -v nginx &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq nginx > /dev/null 2>&1
fi
if ! command -v certbot &> /dev/null; then
    snap install --classic certbot 2>/dev/null || true
    ln -sf /snap/bin/certbot /usr/bin/certbot 2>/dev/null || true
fi

# ── 4. Configure nginx + TLS certificate ──
# HTTP-only config first (for certbot challenge)
cat > /etc/nginx/sites-available/dashboard << 'NGINX_HTTP'
server {
    listen 80;
    server_name train.bitbanshee.com;
    location /.well-known/acme-challenge/ { root /var/www/html; }
    location / { return 301 https://$host$request_uri; }
}
NGINX_HTTP
ln -sf /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/dashboard
rm -f /etc/nginx/sites-enabled/default
systemctl start nginx 2>/dev/null || systemctl reload nginx

# Get cert if we don't have one
if [ ! -f /etc/letsencrypt/live/train.bitbanshee.com/fullchain.pem ]; then
    echo "  Obtaining TLS certificate..."
    sleep 5  # brief wait for DNS propagation
    certbot certonly --webroot -w /var/www/html -d train.bitbanshee.com \
        --non-interactive --agree-tos -m glenn@bitbanshee.com 2>&1 | tail -3
fi

# Full TLS config
cat > /etc/nginx/sites-available/dashboard << 'NGINX_TLS'
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=sse:1m rate=2r/s;

server {
    listen 80;
    server_name train.bitbanshee.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl;
    server_name train.bitbanshee.com;

    ssl_certificate /etc/letsencrypt/live/train.bitbanshee.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/train.bitbanshee.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;

    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-Frame-Options DENY always;
    add_header Referrer-Policy strict-origin-when-cross-origin always;

    location / {
        limit_req zone=general burst=20 nodelay;
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /stream {
        limit_req zone=sse burst=5 nodelay;
        proxy_pass http://127.0.0.1:5000/stream;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_buffering off;
        proxy_cache off;
        proxy_set_header X-Accel-Buffering no;
        proxy_set_header Connection "";
        proxy_http_version 1.1;
        proxy_read_timeout 86400s;
    }
}
NGINX_TLS
nginx -t 2>&1 && systemctl reload nginx
echo "  nginx + TLS: CONFIGURED"

# ── 5. Install Flask if missing ──
sudo -u ubuntu python3 -c "import flask" 2>/dev/null || sudo -u ubuntu pip install --user flask > /dev/null 2>&1

# ── 6. Start web dashboard ──
echo "Starting web dashboard..."
sudo -u ubuntu bash -c "cd $PROJECT && nohup python3 web_dashboard.py --port 5000 --spot-token '$SPOT_TOKEN' > /tmp/dashboard.log 2>&1 &"
sleep 3
curl -sf http://127.0.0.1:5000/api/status > /dev/null && echo "  web dashboard: RUNNING" || echo "  WARNING: web dashboard failed to start"

# ── 7. Start spot price updater (every 5 minutes) ──
echo "Starting spot price updater..."
sudo -u ubuntu bash -c "cd $PROJECT && nohup bash -c 'while true; do bash update-spot-price.sh train.bitbanshee.com \"$SPOT_TOKEN\" > /dev/null 2>&1; sleep 300; done' > /tmp/spot-updater.log 2>&1 &"

# ── 8. Launch training in tmux (resumes from latest checkpoint) ──
echo "Launching training..."
sudo -u ubuntu setsid tmux new-session -d -s training -c "$PROJECT"
sudo -u ubuntu tmux send-keys -t training "export WANDB_API_KEY='$WANDB_API_KEY' HF_TOKEN='$HF_TOKEN' PREPROCESSED_DATA_DIR='$DATA_DIR/preprocessed' CHECKPOINT_DIR='$DATA_DIR/checkpoints' DATA_DIR='$DATA_DIR' PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && python3 -m src.training.joint_trainer --config configs/tiny.yaml" Enter
echo "  training: LAUNCHED in tmux (will resume from latest checkpoint)"

echo ""
echo "=== Bootstrap.sh completed at $(date -u) ==="
echo "=== All services started autonomously ==="
echo "  Dashboard: https://train.bitbanshee.com"
echo "  tmux: tmux attach -t training"
