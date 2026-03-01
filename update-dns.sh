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
echo "DNS update submitted:"
echo "  $RECORD_NAME -> $PUBLIC_IP"
echo "  console.bitbanshee.com -> $PUBLIC_IP (SSH)"
