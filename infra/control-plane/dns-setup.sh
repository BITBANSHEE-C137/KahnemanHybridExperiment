#!/usr/bin/env bash
set -euo pipefail

# ── Validate argument ──────────────────────────────────────────────────────
if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <TUNNEL_UUID>"
  echo "  Example: $0 a1b2c3d4-e5f6-7890-abcd-ef1234567890"
  exit 1
fi

TUNNEL_UUID="$1"
HOSTED_ZONE_ID="Z03629483MIHQSCG59T8J"
RECORD_NAME="lab.bitbanshee.com"
RECORD_VALUE="${TUNNEL_UUID}.cfargotunnel.com"
TTL=300

echo "Creating CNAME record..."
echo "  ${RECORD_NAME} -> ${RECORD_VALUE} (TTL ${TTL})"

# ── Upsert CNAME record ────────────────────────────────────────────────────
CHANGE_BATCH=$(cat <<EOF
{
  "Changes": [
    {
      "Action": "UPSERT",
      "ResourceRecordSet": {
        "Name": "${RECORD_NAME}",
        "Type": "CNAME",
        "TTL": ${TTL},
        "ResourceRecords": [
          {
            "Value": "${RECORD_VALUE}"
          }
        ]
      }
    }
  ]
}
EOF
)

CHANGE_ID=$(aws route53 change-resource-record-sets \
  --hosted-zone-id "${HOSTED_ZONE_ID}" \
  --change-batch "${CHANGE_BATCH}" \
  --query "ChangeInfo.Id" \
  --output text)

echo ""
echo "=== DNS Update Submitted ==="
echo "  Change ID: ${CHANGE_ID}"
echo "  Record:    ${RECORD_NAME} CNAME ${RECORD_VALUE}"
echo "  TTL:       ${TTL}s"
