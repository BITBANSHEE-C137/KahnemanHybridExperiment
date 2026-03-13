#!/usr/bin/env bash
# Updates the Route53 A record for train.bitbanshee.com to this instance's
# public IP. Designed to run on boot (via user-data or systemd) and
# requires Route53 permissions on the instance role.
#
# Usage: ./update-dns.sh

set -euo pipefail

HOSTED_ZONE_ID="Z03629483MIHQSCG59T8J"
RECORD_NAME="train.bitbanshee.com"
TTL=60

# Get public IP from EC2 Instance Metadata Service (IMDSv2)
TOKEN=$(curl -s -X PUT "http://169.254.169.254/latest/api/token" \
  -H "X-aws-ec2-metadata-token-ttl-seconds: 60")
PUBLIC_IP=$(curl -s -H "X-aws-ec2-metadata-token: $TOKEN" \
  "http://169.254.169.254/latest/meta-data/public-ipv4")

if [ -z "$PUBLIC_IP" ]; then
  echo "ERROR: Could not retrieve public IP from IMDS" >&2
  exit 1
fi

echo "Updating $RECORD_NAME -> $PUBLIC_IP"

CHANGE_BATCH=$(cat <<EOF
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "$RECORD_NAME",
        "Type": "A",
        "TTL": $TTL,
        "ResourceRecords": [{"Value": "$PUBLIC_IP"}]
      }
    },
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "console.bitbanshee.com",
        "Type": "A",
        "TTL": $TTL,
        "ResourceRecords": [{"Value": "$PUBLIC_IP"}]
      }
    }
  ]
}
EOF
)

RESULT=$(aws route53 change-resource-record-sets \
  --hosted-zone-id "$HOSTED_ZONE_ID" \
  --change-batch "$CHANGE_BATCH" \
  --region us-east-1 \
  --output json 2>&1)

echo "$RESULT"
echo "Route53 update submitted:"
echo "  $RECORD_NAME -> $PUBLIC_IP"
echo "  console.bitbanshee.com -> $PUBLIC_IP"

# Update Cloudflare DNS (zone is now managed by Cloudflare)
CF_API_KEY=$(aws secretsmanager get-secret-value \
    --secret-id ml-lab/cloudflare-api-key \
    --query 'SecretString' --output text --region us-east-1 2>/dev/null \
    | python3 -c "import sys,json; print(json.load(sys.stdin).get('cloudflare-api-key',''))" 2>/dev/null || echo "")
CF_ZONE_ID="917e7955f5288f7580fe0d5130b2309b"
CF_RECORD_ID="6578c3ebe01bbd37028821d3e52ef9e9"

if [ -n "$CF_API_KEY" ]; then
    CF_RESULT=$(curl -s -X PATCH "https://api.cloudflare.com/client/v4/zones/$CF_ZONE_ID/dns_records/$CF_RECORD_ID" \
        -H "Authorization: Bearer $CF_API_KEY" \
        -H "Content-Type: application/json" \
        --data "{\"content\":\"$PUBLIC_IP\"}" 2>&1)
    echo "$CF_RESULT" | python3 -c "
import sys,json
d=json.load(sys.stdin)
if d.get('success'): print('Cloudflare updated: origin.train.bitbanshee.com ->', d['result']['content'])
else: print('Cloudflare update FAILED:', d.get('errors',''))
" 2>/dev/null || echo "WARNING: Cloudflare DNS update failed"
else
    echo "WARNING: Could not fetch Cloudflare API key"
fi
