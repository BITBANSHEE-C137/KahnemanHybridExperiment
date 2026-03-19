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

STEP_LABELS='["NVMe ephemeral storage","Fetch secrets","Configure environment","Pull latest code","Restore artifacts from S3","Sync preprocessed data","Fix file ownership","Update CloudFront DNS","Start sync daemon","Install nginx","Configure nginx","Install dependencies","Start web dashboard","Setup spot price updater","Setup cost tracker","Setup auto-sitrep","Register Telegram webhook","Launch training"]'

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
sudo mkdir -p "$DATA_DIR"/{hf_cache,checkpoints,checkpoints/v2,checkpoints/v3,logs,benchmarks,eval_metrics,preprocessed}
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
# Generate webhook secret deterministically from bot token
if [ -n "$TELEGRAM_BOT_TOKEN" ]; then
    TELEGRAM_WEBHOOK_SECRET=$(echo -n "$TELEGRAM_BOT_TOKEN" | sha256sum | cut -c1-64)
else
    TELEGRAM_WEBHOOK_SECRET=""
fi
step_done 1

# ── Step 2: Ubuntu user environment ──
step_start 2
echo "Configuring ubuntu user environment..."
# Clean any leftover exports from previous boots (idempotent)
sudo -u ubuntu sed -i '/^export GH_TOKEN/d; /^export CLAUDE_CODE_OAUTH_TOKEN/d; /^export CHECKPOINT_DIR/d; /^export CHECKPOINT_S3_PREFIX/d; /^export EVAL_S3_PREFIX/d; /^export WANDB_API_KEY/d; /^export HF_TOKEN/d; /^export HUGGING_FACE_HUB_TOKEN/d; /^export SPOT_TOKEN/d; /^export CLAUDE_API_KEY/d; /^export TELEGRAM_BOT_TOKEN/d; /^export TELEGRAM_CHAT_ID/d; /^export TELEGRAM_WEBHOOK_SECRET/d' /home/ubuntu/.bashrc

# Inject secrets + version-derived paths (infra constants come from /etc/ml-lab/infra.env)
cat >> /home/ubuntu/.bashrc << BASHRC
export GH_TOKEN="$GH_TOKEN"
export CHECKPOINT_DIR=$DATA_DIR/checkpoints/v4
export CHECKPOINT_S3_PREFIX=checkpoints/v4
export EVAL_S3_PREFIX=eval_metrics/v4
export WANDB_API_KEY="$WANDB_API_KEY"
export HF_TOKEN="$HF_TOKEN"
export HUGGING_FACE_HUB_TOKEN="$HF_TOKEN"
export SPOT_TOKEN="$SPOT_TOKEN"
export CLAUDE_API_KEY="$CLAUDE_API_KEY"
export TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN"
export TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID"
export TELEGRAM_WEBHOOK_SECRET="$TELEGRAM_WEBHOOK_SECRET"
BASHRC

# Git credentials
sudo -u ubuntu bash -c "echo 'https://x-access-token:$GH_TOKEN@github.com' > ~/.git-credentials && git config --global credential.helper store"
step_done 2

# ── Step 3: Pull latest code (clone if not present) ──
step_start 3
if [ ! -d "$PROJECT/.git" ]; then
    echo "Repo not found — cloning from GitHub..."
    sudo -u ubuntu git clone "https://x-access-token:$GH_TOKEN@github.com/BITBANSHEE-C137/KahnemanHybridExperiment.git" "$PROJECT"
else
    sudo -u ubuntu bash -c "cd $PROJECT && git checkout -- . && git clean -fd && git pull --ff-only" || true
fi
step_done 3

# ── Step 3.5: Read active training run config from S3 ──
echo "Checking for active training run..."
ACTIVE_JSON=$(aws s3 cp "s3://$S3_BUCKET/deploy/active.json" - --region "$REGION" 2>/dev/null || echo "")
if [ -n "$ACTIVE_JSON" ] && [ "$ACTIVE_JSON" != "" ]; then
    RUN_ID=$(echo "$ACTIVE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['run_id'])")
    RUN_CONFIG_KEY=$(echo "$ACTIVE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['config_key'])")
    RUN_VERSION=$(echo "$ACTIVE_JSON" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['version'])")
    echo "  Active run: $RUN_VERSION (ID: $RUN_ID)"

    # Download immutable config
    RUN_CONFIG=$(aws s3 cp "s3://$S3_BUCKET/$RUN_CONFIG_KEY" - --region "$REGION" 2>/dev/null || echo "")
    if [ -z "$RUN_CONFIG" ]; then
        echo "FATAL: Could not download config for run $RUN_ID. Idling."
        sleep infinity
        exit 1
    fi

    # Write config as YAML for the trainer
    python3 -c "
import sys, json, yaml
config = json.loads('''$RUN_CONFIG''')
# Extract run meta
meta = config.pop('_run_meta', {})
with open('$PROJECT/configs/active_run.yaml', 'w') as f:
    yaml.dump(config, f, default_flow_style=False)
print('  Config written to configs/active_run.yaml')
# Export meta as env vars
print('RUN_VERSION=' + meta.get('version', '$RUN_VERSION'))
print('RUN_MAX_BUDGET=' + str(meta.get('max_budget', 50)))
print('RUN_MAX_SPOT_PRICE=' + str(meta.get('max_spot_price', 0.75)))
print('RUN_ID=' + meta.get('run_id', '$RUN_ID'))
" > /tmp/run_meta.env
    source /tmp/run_meta.env 2>/dev/null || true
    RUN_CONFIG_FILE="configs/active_run.yaml"
    echo "  Run version: $RUN_VERSION"
else
    echo "No active run found. Idling (fail-closed)."
    # Publish idle beacon
    python3 -c "
import json
from datetime import datetime, timezone
obj = {'status':'idle','reason':'no_active_run','timestamp':datetime.now(timezone.utc).isoformat()}
print(json.dumps(obj))
" > /tmp/bootstrap_beacon.json
    aws s3 cp /tmp/bootstrap_beacon.json "s3://$FALLBACK_BUCKET/bootstrap_beacon.json" \
        --region "$REGION" --content-type "application/json" --cache-control "no-cache" 2>/dev/null || true
    sleep infinity
    exit 0
fi

# Re-export version-specific paths now that RUN_VERSION is known
if [ -n "$RUN_VERSION" ]; then
    sudo -u ubuntu sed -i "s|checkpoints/v4|checkpoints/$RUN_VERSION|g; s|eval_metrics/v4|eval_metrics/$RUN_VERSION|g" /home/ubuntu/.bashrc
    sudo mkdir -p "$DATA_DIR/checkpoints/$RUN_VERSION"
    sudo chown ubuntu:ubuntu "$DATA_DIR/checkpoints/$RUN_VERSION"
fi

# ── Step 4: Restore prior artifacts from S3 ──
step_start 4
echo "Restoring prior artifacts from S3..."
# Restore v2 final checkpoint (needed for v2 benchmarks)
aws s3 cp "s3://$S3_BUCKET/checkpoints/v2/step_50000.pt" "$DATA_DIR/checkpoints/v2/step_50000.pt" --region "$REGION" 2>/dev/null || true
# Restore current version checkpoints (for resume)
aws s3 sync "s3://$S3_BUCKET/checkpoints/$RUN_VERSION/" "$DATA_DIR/checkpoints/$RUN_VERSION/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/logs/" "$DATA_DIR/logs/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/eval_metrics/$RUN_VERSION/" "$DATA_DIR/eval_metrics/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/benchmarks/" "$DATA_DIR/benchmarks/" --region "$REGION" || true
aws s3 sync "s3://$S3_BUCKET/wandb/" "$PROJECT/wandb/" --region "$REGION" || true
echo "Restored checkpoints ($RUN_VERSION):"
ls -lh "$DATA_DIR/checkpoints/$RUN_VERSION/"*.pt 2>/dev/null || echo "  (none)"
echo "v2 final checkpoint:"
ls -lh "$DATA_DIR/checkpoints/v2/step_50000.pt" 2>/dev/null || echo "  (none)"
step_done 4

# ── Step 5: Sync pre-processed training data (prefer persistent EBS, fallback to S3) ──
step_start 5
STATIC_COPIED=false
# Try to attach persistent EBS volume tagged 'ml-lab-static-data' in this AZ
INSTANCE_ID=$(curl -sf http://169.254.169.254/latest/meta-data/instance-id || echo "")
MY_AZ=$(curl -sf http://169.254.169.254/latest/meta-data/placement/availability-zone || echo "")
if [ -n "$INSTANCE_ID" ] && [ -n "$MY_AZ" ]; then
    STATIC_VOL=$(aws ec2 describe-volumes --region "$REGION" \
        --filters "Name=tag:Name,Values=ml-lab-static-data" \
                  "Name=availability-zone,Values=$MY_AZ" \
                  "Name=status,Values=available" \
        --query "Volumes[0].VolumeId" --output text 2>/dev/null || echo "")
    if [ -n "$STATIC_VOL" ] && [ "$STATIC_VOL" != "None" ]; then
        echo "Attaching persistent EBS volume $STATIC_VOL ($MY_AZ)..."
        aws ec2 attach-volume --volume-id "$STATIC_VOL" --instance-id "$INSTANCE_ID" \
            --device /dev/sdf --region "$REGION" > /dev/null 2>&1 || true
        # Wait for device to appear (NVMe rename: /dev/sdf -> /dev/nvme*n1)
        for i in $(seq 1 30); do
            STATIC_DEV=$(lsblk -o NAME,SIZE,TYPE -nr 2>/dev/null | awk '$2=="20G" && $3=="disk" && $1 !~ /nvme0|nvme1/ {print "/dev/"$1; exit}') || true
            [ -n "$STATIC_DEV" ] && break
            sleep 1
        done
        if [ -n "$STATIC_DEV" ]; then
            mkdir -p /mnt/static-data
            mount -o ro,norecovery "$STATIC_DEV" /mnt/static-data 2>/dev/null || true
            if [ -d /mnt/static-data/preprocessed ]; then
                cp -a /mnt/static-data/preprocessed/* "$DATA_DIR/preprocessed/"
                echo "  preprocessed data: COPIED from EBS volume"
                STATIC_COPIED=true
            fi
            if [ -d /mnt/static-data/hf_cache ]; then
                cp -a /mnt/static-data/hf_cache/* "$DATA_DIR/hf_cache/"
                echo "  hf_cache: COPIED from EBS volume"
            fi
            umount /mnt/static-data 2>/dev/null || true
        else
            echo "  WARNING: EBS volume attached but device not found"
        fi
        # Detach so volume is available for next launch
        aws ec2 detach-volume --volume-id "$STATIC_VOL" --region "$REGION" > /dev/null 2>&1 || true
    fi
fi
# Fallback to S3 if EBS copy didn't work
if [ "$STATIC_COPIED" != "true" ]; then
    echo "Syncing pre-processed data from S3..."
    aws s3 sync "s3://$S3_BUCKET/preprocessed/" "$DATA_DIR/preprocessed/" --region "$REGION" || true
fi
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
        --region "$REGION" 2>&1 || echo "WARNING: Route53 DNS update failed"
    echo "  Route53: origin.train.bitbanshee.com -> $INSTANCE_IP"
    echo "  Route53: console.bitbanshee.com -> $INSTANCE_IP"

    # Update Cloudflare DNS (zone is now managed by Cloudflare)
    CF_API_KEY=$(aws secretsmanager get-secret-value \
        --secret-id ml-lab/cloudflare-api-key \
        --query 'SecretString' --output text --region "$REGION" 2>/dev/null \
        | python3 -c "import sys,json; print(json.load(sys.stdin).get('cloudflare-api-key',''))" 2>/dev/null || echo "")
    CF_ZONE_ID="917e7955f5288f7580fe0d5130b2309b"
    CF_RECORD_ID="6578c3ebe01bbd37028821d3e52ef9e9"
    if [ -n "$CF_API_KEY" ]; then
        curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$CF_RECORD_ID" \
            -H "Authorization: Bearer $CF_API_KEY" \
            -H "Content-Type: application/json" \
            --data "{\"content\":\"$INSTANCE_IP\"}" 2>&1 | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('success'): print('  Cloudflare: origin.train.bitbanshee.com ->', d['result']['content'])
else: print('  WARNING: Cloudflare DNS update failed:', d.get('errors',''))
" 2>/dev/null || echo "  WARNING: Cloudflare DNS update failed"
    else
        echo "  WARNING: Could not fetch Cloudflare API key from Secrets Manager"
    fi
else
    echo "  WARNING: Could not determine instance public IP"
fi
step_done 7

# ── Step 8: Start artifact sync daemon ──
step_start 8
echo "Starting sync daemon..."
sudo touch /var/log/artifact-sync.log
sudo chown ubuntu:ubuntu /var/log/artifact-sync.log
sudo -u ubuntu bash -c "cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' EVAL_S3_PREFIX=\"eval_metrics/$RUN_VERSION\" CHECKPOINT_S3_PREFIX=\"checkpoints/$RUN_VERSION\" nohup bash sync-checkpoints.sh >> /var/log/artifact-sync.log 2>&1 &"
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

    location /reports/ {
        alias /home/ubuntu/KahnemanHybridExperiment/infra/reports/;
        index index.html;
        try_files $uri $uri/ =404;
    }
}
NGINX_CF
nginx -t 2>&1 && systemctl reload nginx
echo "  nginx: CONFIGURED (HTTP-only, CloudFront terminates TLS)"
step_done 10

# ── Step 11: Install Python dependencies ──
step_start 11
echo "Installing Python dependencies..."
# Install project requirements (torch is pre-installed on DLAMI, pip will skip it)
if [ -f "$PROJECT/requirements.txt" ]; then
    sudo -u ubuntu pip install --user -r "$PROJECT/requirements.txt" 2>&1 | tail -5
fi
# Flask for web dashboard (not in requirements.txt)
sudo -u ubuntu python3 -c "import flask" 2>/dev/null || sudo -u ubuntu pip install --user flask > /dev/null 2>&1
echo "  dependencies: INSTALLED"
step_done 11

# ── Step 12: Start web dashboard ──
step_start 12
echo "Starting web dashboard..."
sudo -u ubuntu bash -c "cd $PROJECT && TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN' TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID' TELEGRAM_WEBHOOK_SECRET='$TELEGRAM_WEBHOOK_SECRET' FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_BUDGET=75 MAX_SPOT_PRICE=0.75 CHECKPOINT_DIR=\"$DATA_DIR/checkpoints/$RUN_VERSION\" CHECKPOINT_S3_PREFIX=\"checkpoints/$RUN_VERSION\" EVAL_S3_PREFIX=\"eval_metrics/$RUN_VERSION\" nohup python3 web_dashboard.py --port 5000 --spot-token '$SPOT_TOKEN' --telegram-webhook-secret '$TELEGRAM_WEBHOOK_SECRET' > /tmp/dashboard.log 2>&1 &"
sleep 3
curl -sf http://127.0.0.1:5000/api/status > /dev/null && echo "  web dashboard: RUNNING" || echo "  WARNING: web dashboard failed to start"
step_done 12

# ── Step 13: Spot price updater — run now + cron every 5 minutes ──
step_start 13
echo "Setting up spot price updater..."
sudo -u ubuntu bash -c "cd $PROJECT && FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_SPOT_PRICE=0.75 SPOT_TOKEN='$SPOT_TOKEN' bash update-spot-price.sh localhost:5000 >> /tmp/spot-updater.log 2>&1" || true
CRON_LINE="*/5 * * * * cd $PROJECT && FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_SPOT_PRICE=0.75 SPOT_TOKEN='$SPOT_TOKEN' bash update-spot-price.sh localhost:5000 >> /tmp/spot-updater.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v update-spot-price | { cat; echo "$CRON_LINE"; } | sudo -u ubuntu crontab -
echo "  spot price: cron installed (every 5 min)"
step_done 13

# ── Step 14: Cost tracker — init ledger + cron every 5 minutes ──
step_start 14
echo "Setting up cost tracker..."
sudo -u ubuntu bash -c "cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' bash cost-tracker.sh init >> /tmp/cost-tracker.log 2>&1" || true
COST_CRON="*/5 * * * * cd $PROJECT && S3_BUCKET='$S3_BUCKET' DATA_DIR='$DATA_DIR' AWS_DEFAULT_REGION='$REGION' FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a' MAX_BUDGET=75 TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN' TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID' bash cost-tracker.sh update >> /tmp/cost-tracker.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v cost-tracker | { cat; echo "$COST_CRON"; } | sudo -u ubuntu crontab -
echo "  cost tracker: initialized + cron installed (every 5 min)"
step_done 14

# ── Step 15: Setup auto-sitrep cron (every 30 min) ──
step_start 15
echo "Setting up auto-sitrep cron..."
SITREP_CRON="*/30 * * * * cd $PROJECT && TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN' TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID' python3 auto_sitrep.py >> /tmp/auto-sitrep.log 2>&1"
EXISTING=$(sudo -u ubuntu crontab -l 2>/dev/null || true)
echo "$EXISTING" | grep -v auto_sitrep | { cat; echo "$SITREP_CRON"; } | sudo -u ubuntu crontab -
echo "  auto-sitrep: cron installed (every 30 min)"
step_done 15

# ── Step 16: Register Telegram webhook ──
step_start 16
echo "Registering Telegram webhook..."
if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_WEBHOOK_SECRET" ]; then
    WEBHOOK_URL="https://train.bitbanshee.com/api/telegram/webhook"
    curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook" \
        -d "url=${WEBHOOK_URL}" \
        -d "secret_token=${TELEGRAM_WEBHOOK_SECRET}" \
        -d "drop_pending_updates=true" \
        -d "allowed_updates=[\"message\"]" > /dev/null 2>&1 \
        && echo "  Telegram webhook: REGISTERED ($WEBHOOK_URL)" \
        || echo "  WARNING: Telegram webhook registration failed"
else
    echo "  Telegram webhook: SKIPPED (no bot token)"
fi
step_done 16

# ── Run v2 benchmarks if v2 checkpoint exists and no v2 benchmark results yet ──
V2_CKPT="$DATA_DIR/checkpoints/v2/step_50000.pt"
if [ -f "$V2_CKPT" ]; then
    V2_BENCH_EXISTS=$(ls "$DATA_DIR/benchmarks/"*step_50000* 2>/dev/null | head -1)
    if [ -z "$V2_BENCH_EXISTS" ]; then
        echo "Running v2 benchmarks on $V2_CKPT..."
        sudo -u ubuntu bash -c "cd $PROJECT && \
            CHECKPOINT_DIR='$DATA_DIR/checkpoints/v2' DATA_DIR='$DATA_DIR' \
            WANDB_API_KEY='$WANDB_API_KEY' HF_TOKEN='$HF_TOKEN' \
            PREPROCESSED_DATA_DIR='$DATA_DIR/preprocessed' \
            python3 -m scripts.benchmark --config configs/tiny.yaml \
            --checkpoint '$V2_CKPT'" || echo "WARNING: v2 benchmarks failed"
    else
        echo "v2 benchmark results already exist, skipping"
    fi
fi

# ── Step 17: Launch training in tmux (v3) ──
step_start 17
echo "Launching training..."
# Write training env to a file (avoids tmux send-keys line length truncation)
cat > /tmp/train_env.sh << TRAINENV
export WANDB_API_KEY='$WANDB_API_KEY'
export HF_TOKEN='$HF_TOKEN'
export PREPROCESSED_DATA_DIR='$DATA_DIR/preprocessed'
export DATA_DIR='$DATA_DIR'
export PROJECT_DIR='$PROJECT'
export S3_BUCKET='$S3_BUCKET'
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True
export FLEET_ID='fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a'
export TELEGRAM_BOT_TOKEN='$TELEGRAM_BOT_TOKEN'
export TELEGRAM_CHAT_ID='$TELEGRAM_CHAT_ID'
export RUN_ID='${RUN_ID:-}'
export RUN_VERSION='${RUN_VERSION:-v4}'
TRAINENV
chmod 600 /tmp/train_env.sh
chown ubuntu:ubuntu /tmp/train_env.sh
sudo -u ubuntu setsid tmux new-session -d -s training -c "$PROJECT"
# Let the config (tiny.yaml) control checkpoint_dir and s3 prefix — no CLI overrides
sudo -u ubuntu tmux send-keys -t training "source /tmp/train_env.sh && python3 -m src.training.joint_trainer --config ${RUN_CONFIG_FILE:-configs/tiny.yaml}" Enter
echo "  training: LAUNCHED in tmux (v3, resumes from checkpoint if available)"
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
import urllib.request, urllib.parse, json
token = '$TELEGRAM_BOT_TOKEN'
chat_id = '$TELEGRAM_CHAT_ID'
instance_id = '$INSTANCE_ID'
instance_type = '$(curl -sf http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo unknown)'
try:
    ledger = json.load(open('/opt/dlami/nvme/ml-lab/cost/cost_ledger.json'))
    n = len(ledger.get('sessions', []))
    r = n - 1
except Exception:
    n, r = 1, 0
label = f'Instance #{n}' if r == 0 else f'Instance #{n} ({r} recoveries)'
msg = f'*{label} bootstrapped*\nID: {instance_id}\nType: {instance_type}\nAll services started.'
data = urllib.parse.urlencode({'chat_id': chat_id, 'text': msg, 'parse_mode': 'Markdown'}).encode()
urllib.request.urlopen(urllib.request.Request(f'https://api.telegram.org/bot{token}/sendMessage', data=data), timeout=10)
" 2>/dev/null || true
fi

echo ""
echo "=== Bootstrap.sh completed at $(date -u) ===" 
echo "=== All services started autonomously ==="
echo "  Dashboard: https://train.bitbanshee.com"
echo "  tmux: tmux attach -t training"
