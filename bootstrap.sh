#!/bin/bash
set -euo pipefail
GH_TOKEN="$1"
REGION="us-east-1"
S3_BUCKET="ml-lab-004507070771/dual-system-research-data"
PROJECT="/home/ubuntu/KahnemanHybridExperiment"
NVME="/opt/dlami/nvme"
DATA_DIR="$NVME/ml-lab"

# ── Bootstrap status tracking ──
BOOTSTRAP_STATUS="/tmp/bootstrap_status.json"

STEP_LABELS='["NVMe ephemeral storage","Fetch secrets","Configure environment","Pull latest code","Restore artifacts from S3","Sync preprocessed data","Fix file ownership","Update CloudFront DNS","Start sync daemon","Install nginx","Configure nginx","Install Flask","Start web dashboard","Setup spot price updater","Setup cost tracker","Setup auto-sitrep","Run v1 benchmarks (skipped)","Launch training"]'

init_bootstrap_status() {
    python3 -c "
import json, time
labels = json.loads('$STEP_LABELS')
steps = []
for i, label in enumerate(labels):
    steps.append({'id': i, 'label': label, 'status': 'pending', 'started': None, 'elapsed': None})
obj = {'status': 'running', 'started': time.time(), 'steps': steps}
with open('${BOOTSTRAP_STATUS}.tmp', 'w') as f:
    json.dump(obj, f)
" && mv "${BOOTSTRAP_STATUS}.tmp" "$BOOTSTRAP_STATUS"
}

step_start() {
    local n="$1"
    python3 -c "
import json, time
with open('$BOOTSTRAP_STATUS') as f:
    obj = json.load(f)
obj['steps'][$n]['status'] = 'running'
obj['steps'][$n]['started'] = time.time()
with open('${BOOTSTRAP_STATUS}.tmp', 'w') as f:
    json.dump(obj, f)
" && mv "${BOOTSTRAP_STATUS}.tmp" "$BOOTSTRAP_STATUS"
}

step_done() {
    local n="$1"
    python3 -c "
import json, time
with open('$BOOTSTRAP_STATUS') as f:
    obj = json.load(f)
s = obj['steps'][$n]
s['status'] = 'done'
if s['started']:
    s['elapsed'] = round(time.time() - s['started'], 1)
with open('${BOOTSTRAP_STATUS}.tmp', 'w') as f:
    json.dump(obj, f)
" && mv "${BOOTSTRAP_STATUS}.tmp" "$BOOTSTRAP_STATUS"
}

step_fail() {
    local n="$1"
    python3 -c "
import json, time
with open('$BOOTSTRAP_STATUS') as f:
    obj = json.load(f)
s = obj['steps'][$n]
s['status'] = 'failed'
if s['started']:
    s['elapsed'] = round(time.time() - s['started'], 1)
obj['status'] = 'failed'
with open('${BOOTSTRAP_STATUS}.tmp', 'w') as f:
    json.dump(obj, f)
" && mv "${BOOTSTRAP_STATUS}.tmp" "$BOOTSTRAP_STATUS"
}

bootstrap_done() {
    python3 -c "
import json, time
with open('$BOOTSTRAP_STATUS') as f:
    obj = json.load(f)
obj['status'] = 'done'
obj['finished'] = time.time()
with open('${BOOTSTRAP_STATUS}.tmp', 'w') as f:
    json.dump(obj, f)
" && mv "${BOOTSTRAP_STATUS}.tmp" "$BOOTSTRAP_STATUS"
}

echo "=== Bootstrap.sh started at $(date -u) ==="
init_bootstrap_status

# Publish bootstrap beacon to S3 (read by fallback page)
FALLBACK_BUCKET="train-bitbanshee-fallback"
python3 -c "
import json, time
from datetime import datetime, timezone
obj = {'status':'bootstrapping','started':datetime.now(timezone.utc).isoformat()}
print(json.dumps(obj))
" > /tmp/bootstrap_beacon.json
aws s3 cp /tmp/bootstrap_beacon.json "s3://$FALLBACK_BUCKET/bootstrap_beacon.json" \
    --region "$REGION" --content-type "application/json" --cache-control "no-cache" 2>/dev/null || true

# ── Step 0: Ephemeral NVMe setup ──
step_start 0
echo "Setting up ephemeral NVMe at $DATA_DIR..."
sudo mkdir -p "$DATA_DIR"/{hf_cache,checkpoints,checkpoints/v2,logs,benchmarks,eval_metrics,preprocessed}
sudo chown -R ubuntu:ubuntu "$DATA_DIR"
step_done 0

# ── Step 1: Fetch secrets from Secrets Manager ──
step_start 1
echo "Fetching secrets from Secrets Manager..."
WANDB_API_KEY=$(aws secretsmanager get-secret-value --secret-id "ml-lab/wandb-api-key" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
HF_TOKEN=$(aws secretsmanager get-secret-value --secret-id "ml-lab/hf-token" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
SPOT_TOKEN=$(aws secretsmanager get-secret-value --secret-id "ml-lab/dashboard-spot-token" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
CLAUDE_API_KEY=$(aws secretsmanager get-secret-value --secret-id "ml-lab/claude-api-key" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
TELEGRAM_BOT_TOKEN=$(aws secretsmanager get-secret-value --secret-id "ml-lab/telegram-bot-token" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
TELEGRAM_CHAT_ID=$(aws secretsmanager get-secret-value --secret-id "ml-lab/telegram-chat-id" --region "$REGION" --query SecretString --output text 2>/dev/null || echo "")
step_done 1

# ── Step 2: Ubuntu user environment ──
step_start 2
echo "Configuring ubuntu user environment..."
# Clean old env vars
sudo -u ubuntu sed -i '/GH_TOKEN/d; /CLAUDE_CODE_OAUTH_TOKEN/d; /HF_HOME/d; /CHECKPOINT_DIR/d; /CHECKPOINT_S3_PREFIX/d; /WANDB_API_KEY/d; /HF_TOKEN/d; /HUGGING_FACE_HUB_TOKEN/d; /S3_BUCKET/d; /DATA_DIR/d; /AWS_DEFAULT_REGION/d; /PREPROCESSED_DATA_DIR/d; /SPOT_TOKEN/d; /PYTORCH_CUDA_ALLOC_CONF/d; /FLEET_ID/d; /MAX_BUDGET/d; /MAX_SPOT_PRICE/d; /CLAUDE_API_KEY/d; /TELEGRAM_BOT_TOKEN/d; /TELEGRAM_CHAT_ID/d' /home/ubuntu/.bashrc

# Inject env vars
cat >> /home/ubuntu/.bashrc << BASHRC
export GH_TOKEN="$GH_TOKEN"
export HF_HOME=$DATA_DIR/hf_cache
export CHECKPOINT_DIR=$DATA_DIR/checkpoints/v2
export CHECKPOINT_S3_PREFIX=checkpoints/v2
export EVAL_S3_PREFIX=eval_metrics/v2
export WANDB_API_KEY="$WANDB_API_KEY"
export HF_TOKEN="$HF_TOKEN"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
export S3_BUCKET="$S3_BUCKET"
export DATA_DIR="$DATA_DIR"
export AWS_DEFAULT_REGION="$REGION"
export PREPROCESSED_DATA_DIR="$DATA_DIR/preprocessed"
export SPOT_TOKEN="$SPOT_TOKEN"
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export FLEET_ID="fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"
export MAX_BUDGET=50
export MAX_SPOT_PRICE=0.75
export CLAUDE_API_KEY="$CLAUDE_API_KEY"
export TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
export TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
BASHRC

# Git credentials
sudo -u ubuntu bash -c "echo 'https://x-access-token:$GH_TOKEN@github.com' > ~/.git-credentials && git config --global credential.helper store"
step_done 2

# ── Step 3: Pull latest code ──
step_start 3
sudo -u ubuntu bash -c "cd $PROJECT && git checkout -- . && git clean -fd && git pull --ff-only" || true
step_done 3

# ── Step 4: Restore prior artifacts from S3 ──
step_start 4
echo "Restoring prior artifacts from S3..."
aws s3 sync "s3://$S3_BUCKET/checkpoints/v2/" "$DATA_DIR/checkpoints/v2/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/logs/" "$DATA_DIR/logs/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/eval_metrics/v2/" "$DATA_DIR/eval_metrics/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/benchmarks/" "$DATA_DIR/benchmarks/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/wandb/" "$PROJECT/wandb/" --region "$REGION" || true
echo "Restored checkpoints:"
ls -lh "$DATA_DIR/checkpoints/v2/"*.pt 2>/dev/null || echo "  (none)"
step_done 4

# ── Step 5: Sync pre-processed training data from S3 ──
step_start 5
echo "Syncing pre-processed data from S3..."
aws s3 sync "s3://$S3_BUCKET/preprocessed/" "$DATA_DIR/preprocessed/" --region "$REGION" || true
ls -lh "$DATA_DIR/preprocessed/" 2>/dev/null
step_done 5

# ── Step 6: Fix ownership (S3 restores as root) ──
step_start 6
sudo chown -R ubuntu:ubuntu "$DATA_DIR"
sudo chown -R ubuntu:ubuntu "$PROJECT/wandb" 2>/dev/null || true
step_done 6

# ── Step 7: Update CloudFront origin to this instance's IP ──
step_start 7
echo "Updating CloudFront origin..."
INSTANCE_IP=$(curl -sf http://169.254.169.254/latest/meta-data/public-ipv4 || echo "")
CF_DIST_ID="EGWW28IMM7U2T"
if [ -n "$INSTANCE_IP" ]; then
    # Update origin.train.bitbanshee.com + console.bitbanshee.com A records
    CHANGE_BATCH=$(cat <<DNSJSON
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "origin.train.bitbanshee.com",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [{"Value": "$INSTANCE_IP"}]
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "console.bitbanshee.com",
        "Type": "A",
        "TTL": 60,
        "ResourceRecords": [{"Value": "$INSTANCE_IP"}]
      }
    }
  ]
}
DNSJSON
    )
    aws route53 change-resource-record-sets \
        --hosted-zone-id Z03629483MIHQSCG59T8J \
        --change-batch "$CHANGE_BATCH" \
        --region "$REGION" 2>&1 || echo "WARNING: DNS origin update failed"
    echo "  origin.train.bitbanshee.com -> $INSTANCE_IP"
    echo "  console.bitbanshee.com -> $INSTANCE_IP (SSH)"
else
    echo "  WARNING: Could not determine instance public IP"
fi
step_done 7

# ── Step 8: Start artifact sync daemon ──
step_start 8
echo "Starting sync daemon..."
sudo touch /var/log/artifact-sync.log
sudo chown ubuntu:ubuntu /var/log/artifact-sync.log
sudo -u ubuntu bash -c "cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' EVAL_S3_PREFIX='eval_metrics/v2' CHECKPOINT_S3_PREFIX='checkpoints/v2' nohup bash sync-checkpoints.sh >> /var/log/artifact-sync.log 2>&1 &"
sleep 1
pgrep -f sync-checkpoints.sh > /dev/null && echo "  sync daemon: RUNNING" || echo "  WARNING: sync daemon failed to start"
step_done 8

# ── Step 9: Install nginx if missing ──
step_start 9
echo "Setting up nginx (HTTP-only, TLS terminates at CloudFront)..."
if ! command -v nginx &> /dev/null; then
    apt-get update -qq && apt-get install -y -qq nginx > /dev/null 2>&1
fi
step_done 9

# ── Step 10: Configure nginx (HTTP-only proxy — CloudFront handles TLS) ──
step_start 10
ln -sf /etc/nginx/sites-available/dashboard /etc/nginx/sites-enabled/dashboard
rm -f /etc/nginx/sites-enabled/default

cat > /etc/nginx/sites-available/dashboard << 'NGINX_CF'
limit_req_zone $binary_remote_addr zone=general:10m rate=30r/s;
limit_req_zone $binary_remote_addr zone=sse:1m rate=2r/s;

server {
    listen 80;
    server_name _;

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
NGINX_CF
nginx -t 2>&1 && systemctl reload nginx
echo "  nginx: CONFIGURED (HTTP-only, CloudFront terminates TLS)"
step_done 10

# ── Step 11: Install Flask if missing ──
step_start 11
sudo -u ubuntu python3 -c "import flask" 2>/dev/null || sudo -u ubuntu pip install --user flask > /dev/null 2>&1
sudo -u ubuntu pip install --user anthropic > /dev/null 2>&1
step_done 11

# ── Step 12: Start web dashboard ──
step_start 12
echo "Starting web dashboard..."
sudo -u ubuntu bash -c "cd $PROJECT && nohup python3 web_dashboard.py --port 5000 --spot-token '$SPOT_TOKEN' > /tmp/dashboard.log 2>&1 &"
sleep 3
curl -sf http://127.0.0.1:5000/api/status > /dev/null && echo "  web dashboard: RUNNING" || echo "  WARNING: web dashboard failed to start"
step_done 12

# ── Step 13: Spot price updater — run now + cron every 5 minutes ──
step_start 13
echo "Setting up spot price updater..."
sudo -u ubuntu bash -c "cd $PROJECT && FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_SPOT_PRICE=0.75 bash update-spot-price.sh localhost:5000 '$SPOT_TOKEN' >> /tmp/spot-updater.log 2>&1" || true
CRON_LINE="*/5 * * * * cd $PROJECT && FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_SPOT_PRICE=0.75 bash update-spot-price.sh localhost:5000 '$SPOT_TOKEN' >> /tmp/spot-updater.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v update-spot-price | { cat; echo "$CRON_LINE"; } | sudo -u ubuntu crontab -
echo "  spot price: cron installed (every 5 min)"
step_done 13

# ── Step 14: Cost tracker — init ledger + cron every 5 minutes ──
step_start 14
echo "Setting up cost tracker..."
sudo -u ubuntu bash -c "cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' bash cost-tracker.sh init >> /tmp/cost-tracker.log 2>&1" || true
COST_CRON="*/5 * * * * cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_BUDGET=50 bash cost-tracker.sh update >> /tmp/cost-tracker.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v cost-tracker | { cat; echo "$COST_CRON"; } | sudo -u ubuntu crontab -
echo "  cost tracker: initialized + cron installed (every 5 min)"
step_done 14

# ── Step 15: Setup auto-sitrep cron (every 30 min) ──
step_start 15
echo "Setting up auto-sitrep cron..."
SITREP_CRON="*/30 * * * * cd $PROJECT && python3 auto_sitrep.py >> /tmp/auto-sitrep.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v auto_sitrep | { cat; echo "$SITREP_CRON"; } | sudo -u ubuntu crontab -
echo "  auto-sitrep: cron installed (every 30 min)"
step_done 15

# ── Step 16: Run v1 benchmarks ──
step_start 16
echo "  SKIPPED (v1 benchmarks not needed for v2)"
step_done 16

# ── Step 17: Launch training in tmux (fresh start for v2) ──
step_start 17
echo "Launching training..."
sudo -u ubuntu setsid tmux new-session -d -s training -c "$PROJECT"
sudo -u ubuntu tmux send-keys -t training "export WANDB_API_KEY='$WANDB_API_KEY' HF_TOKEN='$HF_TOKEN' PREPROCESSED_DATA_DIR='$DATA_DIR/preprocessed' CHECKPOINT_DIR='$DATA_DIR/checkpoints/v2' CHECKPOINT_S3_PREFIX='checkpoints/v2' EVAL_S3_PREFIX='eval_metrics/v2' DATA_DIR='$DATA_DIR' PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True && python3 -m src.training.joint_trainer --config configs/tiny.yaml" Enter
echo "  training: LAUNCHED in tmux (v2, resumes from latest checkpoint if available)"
step_done 17

bootstrap_done

# Update beacon: bootstrap complete
python3 -c "
import json, time
from datetime import datetime, timezone
obj = {'status':'ready','finished':datetime.now(timezone.utc).isoformat()}
print(json.dumps(obj))
" > /tmp/bootstrap_beacon.json
aws s3 cp /tmp/bootstrap_beacon.json "s3://$FALLBACK_BUCKET/bootstrap_beacon.json" \
    --region "$REGION" --content-type "application/json" --cache-control "no-cache" 2>/dev/null || true

# -- Notify via Telegram --
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
    python3 -c "
import urllib.request, urllib.parse
token = '$TELEGRAM_BOT_TOKEN'
chat_id = '$TELEGRAM_CHAT_ID'
msg = '*Instance bootstrapped*\nIP: $INSTANCE_IP\nType: $(curl -sf http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo unknown)\nAll services started.'
data = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg, 'parse_mode': 'Markdown'}).encode()
urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=data), timeout=10)
" 2>/dev/null || true
fi

echo ""
echo "=== Bootstrap.sh completed at $(date -u) ===" 
echo "=== All services started autonomously ==="
echo "  Dashboard: https://train.bitbanshee.com"
echo "  tmux: tmux attach -t training"
