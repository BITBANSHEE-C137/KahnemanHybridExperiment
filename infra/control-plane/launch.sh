#!/usr/bin/env bash
set -euo pipefail

# ── Variables ───────────────────────────────────────────────────────────────
INSTANCE_TYPE="t3.small"
S3_BUCKET="ml-lab-004507070771"
S3_BOOTSTRAP="s3://${S3_BUCKET}/dual-system-research-data/deploy/control-plane-bootstrap.sh"
REGION="us-east-1"

# Resolve latest Ubuntu 24.04 LTS AMI via SSM
AMI=$(aws ssm get-parameters \
  --names /aws/service/canonical/ubuntu/server/24.04/stable/current/amd64/hvm/ebs-gp3/ami-id \
  --query "Parameters[0].Value" \
  --output text \
  --region "${REGION}")
echo "AMI: ${AMI}"

# Get default VPC
VPC_ID=$(aws ec2 describe-vpcs \
  --filters "Name=isDefault,Values=true" \
  --query "Vpcs[0].VpcId" \
  --output text \
  --region "${REGION}")
echo "VPC: ${VPC_ID}"

# ── 1. Create security group (idempotent) ──────────────────────────────────
SG_ID=$(aws ec2 describe-security-groups \
  --filters "Name=group-name,Values=sg-control-plane" "Name=vpc-id,Values=${VPC_ID}" \
  --query "SecurityGroups[0].GroupId" \
  --output text \
  --region "${REGION}" 2>/dev/null || true)

if [[ "${SG_ID}" == "None" || -z "${SG_ID}" ]]; then
  echo "Creating security group sg-control-plane..."
  SG_ID=$(aws ec2 create-security-group \
    --group-name sg-control-plane \
    --description "Control plane - zero inbound, all outbound" \
    --vpc-id "${VPC_ID}" \
    --query "GroupId" \
    --output text \
    --region "${REGION}")

  aws ec2 create-tags \
    --resources "${SG_ID}" \
    --tags Key=Name,Value=sg-control-plane Key=Project,Value=ml-lab \
    --region "${REGION}"
else
  echo "Security group sg-control-plane already exists: ${SG_ID}"
fi

# ── 2. Ensure no inbound rules ─────────────────────────────────────────────
# Revoke any existing ingress rules (default SGs sometimes have self-referencing rules)
EXISTING_INGRESS=$(aws ec2 describe-security-groups \
  --group-ids "${SG_ID}" \
  --query "SecurityGroups[0].IpPermissions" \
  --output json \
  --region "${REGION}")

if [[ "${EXISTING_INGRESS}" != "[]" ]]; then
  echo "Revoking existing inbound rules..."
  aws ec2 revoke-security-group-ingress \
    --group-id "${SG_ID}" \
    --ip-permissions "${EXISTING_INGRESS}" \
    --region "${REGION}"
fi
echo "Security group ${SG_ID}: zero inbound, all outbound."

# ── 3. Get first public subnet ─────────────────────────────────────────────
SUBNET_ID=$(aws ec2 describe-subnets \
  --filters "Name=vpc-id,Values=${VPC_ID}" "Name=map-public-ip-on-launch,Values=true" \
  --query "Subnets[0].SubnetId" \
  --output text \
  --region "${REGION}")
echo "Subnet: ${SUBNET_ID}"

# ── 4. Upload all deployment artifacts to S3 ─────────────────────────────
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
S3_DEPLOY="s3://${S3_BUCKET}/dual-system-research-data/deploy/control-plane"

echo "Uploading deployment artifacts to S3..."
aws s3 cp "${SCRIPT_DIR}/bootstrap.sh" "${S3_BOOTSTRAP}" --region "${REGION}"
aws s3 sync "${SCRIPT_DIR}/app/" "${S3_DEPLOY}/app/" --region "${REGION}"
aws s3 sync "${SCRIPT_DIR}/systemd/" "${S3_DEPLOY}/systemd/" --region "${REGION}"
aws s3 cp "${SCRIPT_DIR}/claude-md-template.md" "${S3_DEPLOY}/claude-md-template.md" --region "${REGION}"
echo "All artifacts uploaded."

# ── 5. Create user-data script ─────────────────────────────────────────────
USER_DATA=$(cat <<'USERDATA'
#!/bin/bash
set -euo pipefail
LOG="/var/log/control-plane-bootstrap.log"
exec > >(tee -a "${LOG}") 2>&1
echo "=== Control plane bootstrap started at $(date -u) ==="
aws s3 cp s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane-bootstrap.sh /tmp/bootstrap.sh
chmod +x /tmp/bootstrap.sh
/tmp/bootstrap.sh
echo "=== Control plane bootstrap finished at $(date -u) ==="
USERDATA
)

USER_DATA_B64=$(echo "${USER_DATA}" | base64 -w 0)

# ── 6. Launch instance ─────────────────────────────────────────────────────
echo "Launching instance..."
INSTANCE_ID=$(aws ec2 run-instances \
  --instance-type "${INSTANCE_TYPE}" \
  --image-id "${AMI}" \
  --subnet-id "${SUBNET_ID}" \
  --security-group-ids "${SG_ID}" \
  --iam-instance-profile Name=LabOperator \
  --block-device-mappings '[{"DeviceName":"/dev/sda1","Ebs":{"VolumeSize":20,"VolumeType":"gp3","Encrypted":true}}]' \
  --tag-specifications '[{"ResourceType":"instance","Tags":[{"Key":"Name","Value":"ml-lab-control-plane"},{"Key":"Project","Value":"ml-lab"}]}]' \
  --user-data "${USER_DATA_B64}" \
  --associate-public-ip-address \
  --query "Instances[0].InstanceId" \
  --output text \
  --region "${REGION}")

echo "Instance ID: ${INSTANCE_ID}"

# ── 7. Wait for instance running ───────────────────────────────────────────
echo "Waiting for instance to reach 'running' state..."
aws ec2 wait instance-running \
  --instance-ids "${INSTANCE_ID}" \
  --region "${REGION}"

# ── 8. Get public IP ───────────────────────────────────────────────────────
PUBLIC_IP=$(aws ec2 describe-instances \
  --instance-ids "${INSTANCE_ID}" \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text \
  --region "${REGION}")

echo ""
echo "=== Launch Complete ==="
echo "  Instance ID: ${INSTANCE_ID}"
echo "  Public IP:   ${PUBLIC_IP}"
echo "  Type:        ${INSTANCE_TYPE}"
echo "  AMI:         ${AMI}"
echo "  SG:          ${SG_ID}"
echo "  Subnet:      ${SUBNET_ID}"
echo "  No SSH key — access via SSM or cloudflared tunnel only"
