#!/usr/bin/env bash
# Fetches current spot price from AWS and pushes it to the dashboard.
# Run from a machine with AWS CLI access (not the GPU instance).
#
# Usage:  ./update-spot-price.sh [host:port]
# Example: ./update-spot-price.sh 52.90.216.77:5000
#
# Can be cron'd: */15 * * * * /path/to/update-spot-price.sh 52.90.216.77:5000

set -euo pipefail

HOST="${1:-52.90.216.77:5000}"
INST="g6.xlarge"
AZ="us-east-1b"
REGION="us-east-1"

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
# Sort oldest first
hist.sort(key=lambda x: x['Timestamp'])
price_history = []
for p in hist:
    ts = datetime.fromisoformat(p['Timestamp'].replace('Z', '+00:00')).timestamp()
    price_history.append({'timestamp': ts, 'price': float(p['SpotPrice'])})
# Current = most recent
current = float(hist[-1]['SpotPrice'])
print(json.dumps({
    'current_price': current,
    'az': '$AZ',
    'instance_type': '$INST',
    'updated': datetime.now(timezone.utc).isoformat(),
    'price_history': price_history,
}))
")

RESP=$(curl -s -X POST "http://${HOST}/api/spot-price" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

echo "Pushed spot price to $HOST: $RESP"
echo "Current spot: $(echo "$PAYLOAD" | python3 -c "import json,sys; print('$'+str(json.load(sys.stdin).get('current_price','?')))")/hr"
