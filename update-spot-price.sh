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
    http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "g6.xlarge")
  AZ=$(curl -sf -H "X-aws-ec2-metadata-token: $IMDS_TOKEN" \
    http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "us-east-1b")
else
  INST="g6.xlarge"
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
  --output json 2>/dev/null)

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

CURL_ARGS=(-s -X POST "https://${HOST}/api/spot-price" -H "Content-Type: application/json")
if [ -n "$TOKEN" ]; then
  CURL_ARGS+=(-H "Authorization: Bearer ${TOKEN}")
fi

RESP=$(curl "${CURL_ARGS[@]}" -d "$PAYLOAD")

echo "Pushed spot price to $HOST: $RESP"
echo "Current spot: $(echo "$PAYLOAD" | python3 -c "import json,sys; print('$'+str(json.load(sys.stdin).get('current_price','?')))")/hr"
