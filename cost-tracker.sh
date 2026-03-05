#!/usr/bin/env bash
# cost-tracker.sh — Persistent cross-instance cost tracking.
# Maintains a cost ledger in S3 that survives spot terminations.
#
# Usage:
#   cost-tracker.sh init      # Bootstrap: restore ledger, register new session
#   cost-tracker.sh update    # Periodic: update current session cost
#   cost-tracker.sh finalize  # Termination: final update + mark finalized

set -euo pipefail

S3_BUCKET="${S3_BUCKET:-ml-lab-004507070771/dual-system-research-data}"
DATA_DIR="${DATA_DIR:-/opt/dlami/nvme/ml-lab}"
REGION="${AWS_DEFAULT_REGION:-us-east-1}"
PROJECT_DIR="${PROJECT_DIR:-/home/ubuntu/KahnemanHybridExperiment}"

LEDGER_DIR="$DATA_DIR/cost"
LEDGER_FILE="$LEDGER_DIR/cost_ledger.json"
S3_LEDGER="s3://$S3_BUCKET/cost/cost_ledger.json"
SPOT_PRICE_FILE="/tmp/spot_price.json"
TRAINING_RUN="tiny-v2"

mkdir -p "$LEDGER_DIR"

# ── Helpers ───────────────────────────────────────────────────────────────

get_instance_metadata() {
    local imds_token
    imds_token=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
        http://169.254.169.254/latest/api/token 2>/dev/null || echo "")

    if [ -n "$imds_token" ]; then
        INSTANCE_ID=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "unknown")
        INSTANCE_TYPE=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "unknown")
        AZ=$(curl -sf -H "X-aws-ec2-metadata-token: $imds_token" \
            http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "unknown")
    else
        INSTANCE_ID="unknown"
        INSTANCE_TYPE="unknown"
        AZ="unknown"
    fi

    BOOT_TIME=$(python3 -c "
from datetime import datetime, timezone
import subprocess
boot_str = subprocess.check_output(['uptime', '-s'], text=True).strip()
boot_dt = datetime.strptime(boot_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
print(boot_dt.isoformat())
" 2>/dev/null || date -u +%Y-%m-%dT%H:%M:%SZ)
}

get_current_step() {
    local wandb_log step
    wandb_log=$(ls -td "$PROJECT_DIR"/wandb/run-*/files/output.log 2>/dev/null | head -1)
    if [ -n "$wandb_log" ] && [ -f "$wandb_log" ]; then
        step=$(grep -oP '^step:\s*\K[0-9]+' "$wandb_log" | tail -1)
        echo "${step:-0}"
    else
        echo "0"
    fi
}

compute_spot_cost() {
    python3 -c "
import json, time
from datetime import datetime, timezone
import subprocess

boot_str = subprocess.check_output(['uptime', '-s'], text=True).strip()
boot_dt = datetime.strptime(boot_str, '%Y-%m-%d %H:%M:%S').replace(tzinfo=timezone.utc)
boot_ts = boot_dt.timestamp()
now_ts = time.time()

try:
    with open('$SPOT_PRICE_FILE') as f:
        spot = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    print('0.0')
    raise SystemExit(0)

history = sorted(spot.get('price_history', []), key=lambda x: x['timestamp'])
if history:
    total = 0.0
    for i, seg in enumerate(history):
        s = max(seg['timestamp'], boot_ts)
        e = history[i+1]['timestamp'] if i+1 < len(history) else now_ts
        e = min(e, now_ts)
        if s < e:
            total += seg['price'] * (e - s) / 3600
    print(f'{total:.4f}')
elif spot.get('current_price'):
    uptime_h = (now_ts - boot_ts) / 3600
    print(f\"{spot['current_price'] * uptime_h:.4f}\")
else:
    print('0.0')
" 2>/dev/null || echo "0.0"
}

upload_ledger() {
    aws s3 cp "$LEDGER_FILE" "$S3_LEDGER" --region "$REGION" 2>/dev/null || \
        echo "[cost-tracker] WARNING: S3 upload failed"
}

# ── init ──────────────────────────────────────────────────────────────────

cmd_init() {
    echo "[cost-tracker] Initializing cost ledger..."

    # Download existing ledger from S3 (or start fresh)
    aws s3 cp "$S3_LEDGER" "$LEDGER_FILE" --region "$REGION" 2>/dev/null || true

    get_instance_metadata
    local current_step spot_cost
    current_step=$(get_current_step)
    spot_cost=$(compute_spot_cost)

    python3 << PYEOF
import json
from datetime import datetime, timezone

ledger_file = "$LEDGER_FILE"
try:
    with open(ledger_file) as f:
        ledger = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    ledger = {"training_run": "$TRAINING_RUN", "sessions": [], "total_cost": 0.0}

now = datetime.now(timezone.utc).isoformat()

# Finalize any un-finalized sessions from prior instances
for s in ledger["sessions"]:
    if not s.get("finalized", False):
        s["finalized"] = True
        if not s.get("end_time"):
            s["end_time"] = ledger.get("last_updated", now)

# Determine steps_start from last finalized session
steps_start = int("$current_step") if "$current_step" != "0" else 0
if steps_start == 0:
    for s in reversed(ledger["sessions"]):
        if s.get("finalized", False) and s.get("steps_end"):
            steps_start = s["steps_end"]
            break

# Append new session
ledger["sessions"].append({
    "instance_id": "$INSTANCE_ID",
    "instance_type": "$INSTANCE_TYPE",
    "az": "$AZ",
    "boot_time": "$BOOT_TIME",
    "end_time": None,
    "steps_start": steps_start,
    "steps_end": steps_start,
    "spot_cost": float("$spot_cost"),
    "finalized": False,
})

ledger["total_cost"] = round(sum(s.get("spot_cost", 0) for s in ledger["sessions"]), 4)
ledger["last_updated"] = now

with open(ledger_file, "w") as f:
    json.dump(ledger, f, indent=2)
PYEOF

    upload_ledger
    echo "[cost-tracker] Ledger initialized — session registered for $INSTANCE_ID"
}

# ── update ────────────────────────────────────────────────────────────────

cmd_update() {
    if [ ! -f "$LEDGER_FILE" ]; then
        echo "[cost-tracker] No ledger file — run 'init' first"
        return 1
    fi

    get_instance_metadata
    local current_step spot_cost
    current_step=$(get_current_step)
    spot_cost=$(compute_spot_cost)

    python3 << PYEOF
import json
from datetime import datetime, timezone

with open("$LEDGER_FILE") as f:
    ledger = json.load(f)

# Find current session (last un-finalized matching this instance)
for s in reversed(ledger["sessions"]):
    if not s.get("finalized", False) and s["instance_id"] == "$INSTANCE_ID":
        s["spot_cost"] = float("$spot_cost")
        step = int("$current_step") if "$current_step" != "0" else 0
        if step > 0:
            s["steps_end"] = step
            if s.get("steps_start", 0) == 0:
                s["steps_start"] = step
        break

ledger["total_cost"] = round(sum(s.get("spot_cost", 0) for s in ledger["sessions"]), 4)
ledger["last_updated"] = datetime.now(timezone.utc).isoformat()

with open("$LEDGER_FILE", "w") as f:
    json.dump(ledger, f, indent=2)
PYEOF

    upload_ledger

    # Budget circuit breaker
    local total_cost max_budget fleet_id
    total_cost=$(python3 -c "import json; print(json.load(open('$LEDGER_FILE'))['total_cost'])")
    max_budget="${MAX_BUDGET:-50}"
    fleet_id="${FLEET_ID:-fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a}"
    if python3 -c "import sys; sys.exit(0 if float('$total_cost') >= float('$max_budget') else 1)" 2>/dev/null; then
        echo "[cost-tracker] BUDGET EXCEEDED: \$$total_cost >= \$$max_budget — shutting down fleet"
        # Telegram budget alert
        python3 -c "
import sys
sys.path.insert(0, '$PROJECT_DIR')
from auto_sitrep import send_telegram
send_telegram('*BUDGET EXCEEDED*
Total cost: \$$total_cost >= limit \$$max_budget
Fleet shutdown initiated.')
" 2>/dev/null || true
        aws ec2 modify-fleet --fleet-id "$fleet_id" \
            --target-capacity-specification TotalTargetCapacity=0,SpotTargetCapacity=0 \
            --region "$REGION" 2>&1 || echo "[cost-tracker] WARNING: Fleet shutdown failed"
    fi
}

# ── finalize ──────────────────────────────────────────────────────────────

cmd_finalize() {
    if [ ! -f "$LEDGER_FILE" ]; then
        echo "[cost-tracker] No ledger file — nothing to finalize"
        return 0
    fi

    get_instance_metadata
    local current_step spot_cost
    current_step=$(get_current_step)
    spot_cost=$(compute_spot_cost)

    python3 << PYEOF
import json
from datetime import datetime, timezone

with open("$LEDGER_FILE") as f:
    ledger = json.load(f)

now = datetime.now(timezone.utc).isoformat()

for s in reversed(ledger["sessions"]):
    if not s.get("finalized", False) and s["instance_id"] == "$INSTANCE_ID":
        s["spot_cost"] = float("$spot_cost")
        step = int("$current_step") if "$current_step" != "0" else 0
        if step > 0:
            s["steps_end"] = step
        s["end_time"] = now
        s["finalized"] = True
        break

ledger["total_cost"] = round(sum(s.get("spot_cost", 0) for s in ledger["sessions"]), 4)
ledger["last_updated"] = now

with open("$LEDGER_FILE", "w") as f:
    json.dump(ledger, f, indent=2)
PYEOF

    upload_ledger
    echo "[cost-tracker] Session finalized for $INSTANCE_ID"
}

# ── Main ──────────────────────────────────────────────────────────────────
case "${1:-}" in
    init)     cmd_init ;;
    update)   cmd_update ;;
    finalize) cmd_finalize ;;
    *)        echo "Usage: $0 {init|update|finalize}"; exit 1 ;;
esac
