#!/usr/bin/env bash
set -euo pipefail

# ── Route53 JSON → BIND Zone File for Cloudflare Import ─────────────────────
#
# Usage:
#   aws route53 list-resource-record-sets \
#     --hosted-zone-id Z03629483MIHQSCG59T8J --output json > route53-export.json
#   ./route53-to-bind.sh route53-export.json > bitbanshee.com.zone
#
# Then upload bitbanshee.com.zone to Cloudflare's DNS → Import tool.
#
# Handles:
#   - AWS Alias A records → CNAME records (for CloudFront distributions)
#   - Standard A, AAAA, CNAME, MX, TXT records → BIND format verbatim
#   - Skips NS and SOA (Cloudflare replaces these)
#   - Multi-value TXT records (SPF, DKIM, DMARC, Replit verify, SES verify)
#   - Quoted TXT values preserved correctly
# ─────────────────────────────────────────────────────────────────────────────

DOMAIN="bitbanshee.com"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <route53-export.json>" >&2
  echo "" >&2
  echo "Generate the input file with:" >&2
  echo "  aws route53 list-resource-record-sets \\" >&2
  echo "    --hosted-zone-id Z03629483MIHQSCG59T8J \\" >&2
  echo "    --output json > route53-export.json" >&2
  exit 1
fi

INPUT_FILE="$1"

if [[ ! -f "$INPUT_FILE" ]]; then
  echo "Error: File not found: $INPUT_FILE" >&2
  exit 1
fi

if ! command -v jq &>/dev/null; then
  echo "Error: jq is required. Install with: sudo apt install jq" >&2
  exit 1
fi

# Validate JSON structure
if ! jq -e '.ResourceRecordSets' "$INPUT_FILE" &>/dev/null; then
  echo "Error: Invalid Route53 export (missing ResourceRecordSets)" >&2
  exit 1
fi

echo ";; ─────────────────────────────────────────────────────────────────"
echo ";; BIND zone file for ${DOMAIN}"
echo ";; Generated from Route53 zone Z03629483MIHQSCG59T8J"
echo ";; Date: $(date -u '+%Y-%m-%d %H:%M:%S UTC')"
echo ";; Import this file into Cloudflare DNS"
echo ";;"
echo ";; IMPORTANT after import:"
echo ";;   - Set CloudFront CNAMEs to DNS-only (grey cloud)"
echo ";;   - Set lab.bitbanshee.com to Proxied (orange cloud)"
echo ";; ─────────────────────────────────────────────────────────────────"
echo ""
echo "\$ORIGIN ${DOMAIN}."
echo ""

SKIPPED=0
CONVERTED=0
COPIED=0

# Process each record set (use process substitution to avoid subshell counter issue)
while IFS= read -r record; do
  name=$(echo "$record" | jq -r '.Name')
  type=$(echo "$record" | jq -r '.Type')
  ttl=$(echo "$record" | jq -r '.TTL // 300')

  # Strip trailing dot for display, keep for BIND format
  display_name="${name%.}"

  # Skip NS and SOA — Cloudflare replaces these
  if [[ "$type" == "NS" || "$type" == "SOA" ]]; then
    echo ";; SKIPPED: ${display_name} ${type} (Cloudflare replaces)" >&2
    ((SKIPPED++)) || true
    continue
  fi

  # Check if this is an AWS Alias record
  is_alias=$(echo "$record" | jq -r '.AliasTarget // empty')

  if [[ -n "$is_alias" ]]; then
    # ── AWS Alias record → Convert to CNAME ──────────────────────────
    alias_target=$(echo "$record" | jq -r '.AliasTarget.DNSName')
    # Strip trailing dot from alias target for BIND CNAME value
    alias_target="${alias_target%.}"

    echo ";; Converted from AWS Alias ${type} → CNAME (set DNS-only in Cloudflare!)"
    echo "${name}  ${ttl}  IN  CNAME  ${alias_target}."
    echo ""

    echo ";; CONVERTED: ${display_name} Alias ${type} → CNAME ${alias_target}" >&2
    ((CONVERTED++)) || true
  else
    # ── Standard record — emit verbatim ──────────────────────────────
    values=$(echo "$record" | jq -r '.ResourceRecords[]?.Value // empty')

    if [[ -z "$values" ]]; then
      echo ";; WARNING: ${display_name} ${type} has no resource records (skipped)" >&2
      ((SKIPPED++)) || true
      continue
    fi

    # Read values into array to avoid nested pipe subshell
    while IFS= read -r value; do
      case "$type" in
        TXT)
          # TXT values from Route53 are already quoted — pass through
          # If not quoted, add quotes
          if [[ "$value" == \"* ]]; then
            echo "${name}  ${ttl}  IN  TXT  ${value}"
          else
            echo "${name}  ${ttl}  IN  TXT  \"${value}\""
          fi
          ;;
        MX)
          # MX values from Route53 include priority: "10 mail.example.com"
          echo "${name}  ${ttl}  IN  MX  ${value}"
          ;;
        CNAME)
          # Ensure trailing dot on CNAME target
          target="${value%.}"
          echo "${name}  ${ttl}  IN  CNAME  ${target}."
          ;;
        A|AAAA)
          echo "${name}  ${ttl}  IN  ${type}  ${value}"
          ;;
        *)
          echo "${name}  ${ttl}  IN  ${type}  ${value}"
          ;;
      esac
    done < <(echo "$record" | jq -r '.ResourceRecords[].Value')
    echo ""

    ((COPIED++)) || true
  fi
done < <(jq -c '.ResourceRecordSets[]' "$INPUT_FILE")

echo "" >&2
echo "── Summary ──────────────────────────────────────────────────────" >&2
echo "  Copied:    ${COPIED} record sets" >&2
echo "  Converted: ${CONVERTED} AWS Alias → CNAME" >&2
echo "  Skipped:   ${SKIPPED} (NS/SOA)" >&2
echo "" >&2
echo "Next steps:" >&2
echo "  1. Import this zone file in Cloudflare Dashboard → DNS → Import" >&2
echo "  2. Verify all records appear (expect ~20 records)" >&2
echo "  3. Set CloudFront CNAMEs to DNS-only (grey cloud):" >&2
echo "     - bitbanshee.com → dpkv71qc5tnrc.cloudfront.net" >&2
echo "     - www.bitbanshee.com → dpkv71qc5tnrc.cloudfront.net" >&2
echo "     - train.bitbanshee.com → d13o6skoljbioe.cloudfront.net" >&2
echo "  4. Add lab.bitbanshee.com CNAME manually (Proxied, orange cloud)" >&2
echo "  5. Set SSL/TLS mode to Full (strict)" >&2
echo "  6. Change nameservers at registrar ONLY after verifying all records" >&2
