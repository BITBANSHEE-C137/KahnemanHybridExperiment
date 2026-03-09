#!/usr/bin/env bash
set -euo pipefail

# ── Get AWS account ID dynamically ──────────────────────────────────────────
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
echo "AWS Account ID: ${ACCOUNT_ID}"

# ── Resolve script directory ────────────────────────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# ── 1. Create LabOperatorRole (EC2 trust policy for instance profile) ───────
EC2_TRUST_POLICY='{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": { "Service": "ec2.amazonaws.com" },
      "Action": "sts:AssumeRole"
    }
  ]
}'

if aws iam get-role --role-name LabOperatorRole &>/dev/null; then
  echo "LabOperatorRole already exists — skipping creation."
else
  echo "Creating LabOperatorRole..."
  aws iam create-role \
    --role-name LabOperatorRole \
    --assume-role-policy-document "${EC2_TRUST_POLICY}" \
    --description "ML lab control-plane operator role (read-only + fleet manage)"
fi

# ── 2. Attach operator inline policy ────────────────────────────────────────
echo "Attaching inline policy OperatorPolicy to LabOperatorRole..."
aws iam put-role-policy \
  --role-name LabOperatorRole \
  --policy-name OperatorPolicy \
  --policy-document "file://${SCRIPT_DIR}/operator-policy.json"

# ── 3. Create LabAdminRole with trust policy ────────────────────────────────
if aws iam get-role --role-name LabAdminRole &>/dev/null; then
  echo "LabAdminRole already exists — skipping creation."
else
  echo "Creating LabAdminRole..."
  aws iam create-role \
    --role-name LabAdminRole \
    --assume-role-policy-document "file://${SCRIPT_DIR}/admin-trust-policy.json" \
    --max-session-duration 3600 \
    --description "ML lab admin role (elevated, 1-hour sessions)"
fi

# ── 4. Attach admin inline policy ──────────────────────────────────────────
echo "Attaching inline policy AdminPolicy to LabAdminRole..."
aws iam put-role-policy \
  --role-name LabAdminRole \
  --policy-name AdminPolicy \
  --policy-document "file://${SCRIPT_DIR}/admin-policy.json"

# ── 5. Create instance profile and add role ─────────────────────────────────
if aws iam get-instance-profile --instance-profile-name LabOperator &>/dev/null; then
  echo "Instance profile LabOperator already exists — skipping creation."
else
  echo "Creating instance profile LabOperator..."
  aws iam create-instance-profile --instance-profile-name LabOperator
fi

# Add role to instance profile (idempotent — fails silently if already added)
if aws iam add-role-to-instance-profile \
    --instance-profile-name LabOperator \
    --role-name LabOperatorRole 2>/dev/null; then
  echo "Added LabOperatorRole to LabOperator instance profile."
else
  echo "LabOperatorRole already in LabOperator instance profile — skipping."
fi

# ── Summary ─────────────────────────────────────────────────────────────────
echo ""
echo "=== IAM Setup Complete ==="
echo "  Role:              LabOperatorRole"
echo "  Inline policy:     OperatorPolicy"
echo "  Role:              LabAdminRole"
echo "  Inline policy:     AdminPolicy"
echo "  Instance profile:  LabOperator"
echo "  Account:           ${ACCOUNT_ID}"
echo ""
echo "LabOperatorRole ARN: arn:aws:iam::${ACCOUNT_ID}:role/LabOperatorRole"
echo "LabAdminRole ARN:    arn:aws:iam::${ACCOUNT_ID}:role/LabAdminRole"
