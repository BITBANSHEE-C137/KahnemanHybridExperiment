#!/usr/bin/env bash
# Fetches current spot price from AWS and pushes it to the dashboard.
# Auto-detects instance type and AZ from IMDS when running on EC2.
#
# Usage:  ./update-spot-price.sh [host] [token]
# Example: ./update-spot-price.sh train.bitbanshee.com mytoken
#
# Token can also be set via SPOT_TOKEN env var.
# Can be cron'd: */15 * * * * SPOT_TOKEN=xxx /path/to/update-spot-price.sh

set -euo pipefail

HOST="${1:-train.bitbanshee.com}"
TOKEN="${2:-${SPOT_TOKEN:-}}"
REGION="us-east-1"

# Auto-detect instance type and AZ from IMDS (falls back to defaults)
IMDS_TOKEN=$(curl -sf -X PUT -H "X-aws-ec2-metadata-token-ttl-seconds: 30" \
  http://169.254.169.254/latest/api/token 2>/dev/null || echo "")
if [ -n "$IMDS_TOKEN" ]; then
  INST=$(curl -sf -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" \
    http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "g5.xlarge")
  AZ=$(curl -sf -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" \
    http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "us-east-1b")
else
  INST="g5.xlarge"
  AZ="us-east-1b"
fi

if [ -z "$TOKEN" ]; then
  echo "Warning: no token provided. POST may be rejected." >&2
  echo "Usage: $0 [host] [token]  (or set SPOT_TOKEN env var)" >&2
fi

PRICES=$(aws ec2 describe-spot-price-history \
  --instance-types "$INST" \
  --product-descriptions "Linux/UNIX" \
  --availability-zone "$AZ" \
  --region "$REGION" \
  --max-items 50 \
  --output json 2>/dev/null) || true

if [ -z "$PRICES" ]; then
  echo "No spot price data returned for $INST in $AZ" >&2
  exit 0
fi

PAYLOAD=$(echo "$PRICES" | python3 -c "
import json, sys
from datetime import datetime, timezone
d = json.load(sys.stdin)
hist = d['SpotPriceHistory']
if not hist:
    print('{}')
    sys.exit(0)
hist.sort(key=lambda x: x['Timestamp'])
price_history = []
for p in hist:
    ts = datetime.fromisoformat(p['Timestamp'].replace('Z', '+00:00')).timestamp()
    price_history.append({'timestamp': ts, 'price': float(p['SpotPrice'])})
current = float(hist[-1]['SpotPrice'])
print(json.dumps({
    'current_price': current,
    'az': '$AZ',
    'instance_type': '$INST',
    'updated': datetime.now(timezone.utc).isoformat(),
    'price_history': price_history,
}))
")

# Spot price ceiling circuit breaker
MAX_SPOT_PRICE="${MAX_SPOT_PRICE:-0.75}"
FLEET_ID="${FLEET_ID:-fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a}"
CURRENT_PRICE=$(echo "$PAYLOAD" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('current_price', 0))" 2>/dev/null || echo "0")
if python3 -c "import sys; sys.exit(0 if float('$CURRENT_PRICE') > 0 and float('$CURRENT_PRICE') >= float('$MAX_SPOT_PRICE') else 1)" 2>/dev/null; then
    echo "[spot-price] PRICE CEILING HIT: \$$CURRENT_PRICE/hr >= \$$MAX_SPOT_PRICE/hr — shutting down fleet"
    # Telegram alert
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    python3 -c "import sys; sys.path.insert(0, '$SCRIPT_DIR'); from auto_sitrep import send_telegram; send_telegram('*SPOT PRICE CEILING HIT*\nRate: \$$CURRENT_PRICE/hr >= ceiling \$$MAX_SPOT_PRICE/hr\nFleet shutdown initiated.')" 2>/dev/null || true
    aws ec2 modify-fleet --fleet-id "$FLEET_ID" \
        --target-capacity-specification TotalTargetCapacity=0,SpotTargetCapacity=0 \
        --region us-east-1 2>&1 || echo "[spot-price] WARNING: Fleet shutdown failed"
fi

SCHEME="https"; [[ "$HOST" == localhost* ]] && SCHEME="http"; CURL_ARGS=(-s -X POST "${SCHEME}://${HOST}/api/spot-price" -H "Content-Type: application/json")
if [ -n "$TOKEN" ]; then
  CURL_ARGS+=(-H "Authorization: Bearer ${TOKEN}")
fi

RESP=$(curl "${CURL_ARGS[@]}" -d "$PAYLOAD")

echo "Pushed spot price to $HOST: $RESP"
echo "Current spot: $(echo "$PAYLOAD" | python3 -c "import json,sys; print('$'+str(json.load(sys.stdin).get('current_price','?')))")/hr"
