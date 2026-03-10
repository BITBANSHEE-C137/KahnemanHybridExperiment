#!/usr/bin/env bash
# Control Plane Bootstrap  -- 16-step autonomous setup
# Deployed to: s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane-bootstrap.sh
# Runs as root via EC2 user-data
set -euo pipefail

# ── Constants ────────────────────────────────────────────────────────────────
REGION="us-east-1"
ACCOUNT_ID="004507070771"
S3_BUCKET="ml-lab-004507070771"
S3_PREFIX="dual-system-research-data"
FLEET_ID="fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a"
ZONE_ID="Z03629483MIHQSCG59T8J"
GITHUB_REPO="BITBANSHEE-C137/KahnemanHybridExperiment"
OPERATOR_USER="claude-operator"
CONTROL_PLANE_DIR="/opt/control-plane"
STATUS_FILE="/var/log/control-plane-status.json"
TOTAL_STEPS=16

# ── Status Tracking ─────────────────────────────────────────────────────────
update_status() {
    local step=$1 name=$2 status=$3
    printf '{"step": %s, "total": %s, "name": "%s", "status": "%s", "timestamp": "%s"}\n' \
        "$step" "$TOTAL_STEPS" "$name" "$status" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
        > "$STATUS_FILE"
}

trap_err() {
    local step=${CURRENT_STEP:-0}
    local name=${CURRENT_NAME:-unknown}
    update_status "$step" "$name" "failed"
    echo "FATAL: Step ${step} (${name}) failed at line $1"
    if [[ -n "${TELEGRAM_BOT_TOKEN:-}" && -n "${TELEGRAM_CHAT_ID:-}" ]]; then
        local msg="Control plane bootstrap FAILED -- Step ${step}: ${name} -- Line: $1"
        curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="${TELEGRAM_CHAT_ID}" --data-urlencode text="${msg}" 2>/dev/null || true
    fi
    exit 1
}
trap 'trap_err $LINENO' ERR

run_step() {
    local step=$1 name=$2 func=$3
    CURRENT_STEP=$step
    CURRENT_NAME=$name
    echo ""
    echo "================================================================"
    echo "=== Step ${step}/${TOTAL_STEPS}: ${name}"
    echo "================================================================"
    local start_ts; start_ts=$(date +%s)
    update_status "$step" "$name" "running"
    $func
    local end_ts; end_ts=$(date +%s)
    echo "--- Step ${step} complete ($((end_ts - start_ts))s) ---"
    update_status "$step" "$name" "complete"
}

# ── Pre-step: Create operator user ──────────────────────────────────────────
echo "=== Pre-step: Creating ${OPERATOR_USER} user ==="
if ! id "$OPERATOR_USER" &>/dev/null; then
    useradd -m -s /bin/bash "$OPERATOR_USER"
    usermod -aG sudo "$OPERATOR_USER"
fi
mkdir -p "/home/${OPERATOR_USER}"/{lab,icloud,.ssh,.config/rclone,.aws,.npm-global,.local/bin}

# ── Step Functions ───────────────────────────────────────────────────────────

step_0_system_packages() {
    export DEBIAN_FRONTEND=noninteractive
    apt-get update -qq
    apt-get install -y -qq \
        tmux curl git jq python3 python3-pip python3-venv \
        fuse3 sqlite3 unzip htop ca-certificates gnupg
    if ! aws --version 2>&1 | grep -q "aws-cli/2"; then
        curl -fsSL "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o /tmp/awscliv2.zip
        unzip -qo /tmp/awscliv2.zip -d /tmp
        /tmp/aws/install --update
        rm -rf /tmp/aws /tmp/awscliv2.zip
    fi
}

step_1_swap() {
    if [[ ! -f /swapfile ]]; then
        fallocate -l 1G /swapfile
        chmod 600 /swapfile
        mkswap /swapfile
        swapon /swapfile
        echo '/swapfile none swap sw 0 0' >> /etc/fstab
    else
        echo "Swap already exists, skipping"
    fi
}

step_2_fetch_secrets() {
    mkdir -p /etc/cloudflared

    get_secret() {
        aws secretsmanager get-secret-value \
            --secret-id "$1" --query SecretString --output text --region "$REGION"
    }

    # Cloudflare tunnel token (remotely managed tunnel)
    CF_TUNNEL_TOKEN=$(get_secret "ml-lab/cloudflare-tunnel-token")
    echo "${CF_TUNNEL_TOKEN}" > /etc/cloudflared/tunnel-token
    chmod 600 /etc/cloudflared/tunnel-token

    ANTHROPIC_API_KEY=$(get_secret "ml-lab/claude-api-key")
    TELEGRAM_BOT_TOKEN=$(get_secret "ml-lab/telegram-bot-token")
    TELEGRAM_CHAT_ID=$(get_secret "ml-lab/telegram-chat-id")
    GITHUB_TOKEN=$(get_secret "ml-lab/github-token")
    CF_POLICY_AUD=$(get_secret "ml-lab/cf-policy-aud")

    # iCloud credentials — deferred to v2, non-fatal
    ICLOUD_APPLE_ID=$(get_secret "ml-lab/icloud-apple-id" 2>/dev/null) || ICLOUD_APPLE_ID=""
    ICLOUD_APP_PASSWORD=$(get_secret "ml-lab/icloud-app-password" 2>/dev/null) || ICLOUD_APP_PASSWORD=""

    get_secret "ml-lab/gpu-ssh-key" > "/home/${OPERATOR_USER}/.ssh/gpu-key.pem"
    chmod 600 "/home/${OPERATOR_USER}/.ssh/gpu-key.pem"

    # Set root password from Secrets Manager
    ROOT_PW=$(get_secret "ml-lab/control-plane-root" | jq -r '.Password')
    echo "root:${ROOT_PW}" | chpasswd
    echo "Root password set from Secrets Manager"
    unset ROOT_PW

    export ANTHROPIC_API_KEY TELEGRAM_BOT_TOKEN TELEGRAM_CHAT_ID
    export GITHUB_TOKEN ICLOUD_APPLE_ID ICLOUD_APP_PASSWORD CF_POLICY_AUD
}

step_3_configure_environment() {
    {
        echo "ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}"
        echo "TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}"
        echo "TELEGRAM_CHAT_ID=${TELEGRAM_CHAT_ID}"
        echo "GITHUB_TOKEN=${GITHUB_TOKEN}"
        echo "CF_TEAM_DOMAIN=bitbanshee-c137"
        echo "CF_POLICY_AUD=${CF_POLICY_AUD}"
        echo "AWS_DEFAULT_REGION=${REGION}"
        echo "FLEET_ID=${FLEET_ID}"
        echo "S3_BUCKET=${S3_BUCKET}"
    } > "/home/${OPERATOR_USER}/.env"
    chmod 600 "/home/${OPERATOR_USER}/.env"

    {
        echo ''
        echo '# Control plane environment'
        echo 'set -o vi'
        echo 'export PATH="$HOME/.local/bin:$HOME/.npm-global/bin:$PATH"'
        echo 'source ~/.env 2>/dev/null || true'
    } >> "/home/${OPERATOR_USER}/.bashrc"

    su - "$OPERATOR_USER" -c "git config --global credential.helper store"
    echo "https://${GITHUB_TOKEN}@github.com" > "/home/${OPERATOR_USER}/.git-credentials"
    chmod 600 "/home/${OPERATOR_USER}/.git-credentials"
    chown "$OPERATOR_USER:$OPERATOR_USER" "/home/${OPERATOR_USER}/.git-credentials"
}

step_4_install_nodejs_claude() {
    # Stop baked services from AMI so binaries can be updated
    systemctl stop ttyd ttyd-shell controlplane-api cloudflared 2>/dev/null || true

    if ! node --version 2>/dev/null | grep -q "v20"; then
        curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
        apt-get install -y -qq nodejs
    else
        echo "Node.js already installed: $(node --version)"
    fi
    # Fix ownership before npm install (pre-step creates dirs as root)
    chown -R "${OPERATOR_USER}:${OPERATOR_USER}" "/home/${OPERATOR_USER}/"
    su - "$OPERATOR_USER" -c "mkdir -p ~/.npm-global && npm config set prefix ~/.npm-global"
    su - "$OPERATOR_USER" -c "npm install -g @anthropic-ai/claude-code"
    echo "Claude Code installed"
}

step_5_install_cloudflared() {
    curl -fsSL https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64.deb \
        -o /tmp/cloudflared.deb
    dpkg -i /tmp/cloudflared.deb
    rm /tmp/cloudflared.deb
    echo "Cloudflared installed (remotely managed tunnel)"
}

step_6_install_ttyd() {
    local ttyd_version="1.7.7"
    if [[ -x /usr/local/bin/ttyd ]]; then
        echo "ttyd already installed, skipping download"
    else
        curl -fsSL "https://github.com/tsl0922/ttyd/releases/download/${ttyd_version}/ttyd.x86_64" \
            -o /usr/local/bin/ttyd
        chmod +x /usr/local/bin/ttyd
    fi
    echo "ttyd ${ttyd_version} ready"
}

step_7_install_rclone() {
    if command -v rclone &>/dev/null; then
        echo "rclone already installed: $(rclone version --check 2>/dev/null | head -1 || rclone --version | head -1)"
    else
        curl -fsSL https://rclone.org/install.sh | bash
    fi

    if [[ -z "${ICLOUD_APPLE_ID:-}" ]]; then
        echo "SKIP: iCloud credentials not set — deferring to v2"
        return 0
    fi

    mkdir -p "/home/${OPERATOR_USER}/.config/rclone"
    {
        echo "[icloud]"
        echo "type = iclouddrive"
        echo "apple_id = ${ICLOUD_APPLE_ID}"
        echo "password = ${ICLOUD_APP_PASSWORD}"
    } > "/home/${OPERATOR_USER}/.config/rclone/rclone.conf"
    chmod 600 "/home/${OPERATOR_USER}/.config/rclone/rclone.conf"

    mkdir -p "/home/${OPERATOR_USER}/icloud"

    if ! grep -q "^user_allow_other" /etc/fuse.conf 2>/dev/null; then
        echo "user_allow_other" >> /etc/fuse.conf
    fi
}

step_8_install_python_deps() {
    pip3 install --break-system-packages --ignore-installed typing-extensions
    pip3 install --break-system-packages \
        fastapi==0.115.6 \
        "uvicorn[standard]==0.34.0" \
        boto3==1.36.7 \
        "python-jose[cryptography]==3.3.0" \
        pydantic==2.10.5 \
        httpx==0.28.1 \
        python-multipart==0.0.22 \
        websockets==16.0
}

step_9_setup_operator_dirs() {
    mkdir -p "/home/${OPERATOR_USER}"/{lab,icloud,.ssh,.config/rclone,.aws,.npm-global,.local/bin}
    mkdir -p "${CONTROL_PLANE_DIR}/static"
    chmod 700 "/home/${OPERATOR_USER}/.ssh"
    chown -R "${OPERATOR_USER}:${OPERATOR_USER}" "/home/${OPERATOR_USER}/"
    chown -R "${OPERATOR_USER}:${OPERATOR_USER}" "${CONTROL_PLANE_DIR}/"
}

step_10_deploy_app() {
    # Deploy app from GitHub (source of truth)
    local GH_RAW="https://raw.githubusercontent.com/${GITHUB_REPO}/main/infra/control-plane/app"
    local GH_API="https://api.github.com/repos/${GITHUB_REPO}/contents/infra/control-plane/app"
    local AUTH="Authorization: token ${GITHUB_TOKEN}"

    # Download all top-level app files
    curl -fsSL -H "${AUTH}" "${GH_API}" | \
        jq -r '.[] | select(.type=="file") | .name' | while read -r fname; do
            curl -fsSL -H "${AUTH}" "${GH_RAW}/${fname}" -o "${CONTROL_PLANE_DIR}/${fname}"
        done

    # Download static files
    mkdir -p "${CONTROL_PLANE_DIR}/static"
    curl -fsSL -H "${AUTH}" "${GH_API}/static" | \
        jq -r '.[] | select(.type=="file") | .name' | while read -r fname; do
            curl -fsSL -H "${AUTH}" "${GH_RAW}/static/${fname}" -o "${CONTROL_PLANE_DIR}/static/${fname}"
        done

    chown -R "${OPERATOR_USER}:${OPERATOR_USER}" "${CONTROL_PLANE_DIR}/"
    echo "App deployed from GitHub to ${CONTROL_PLANE_DIR}/"
    ls -la "${CONTROL_PLANE_DIR}/"
}

step_11_write_claude_md() {
    local AUTH="Authorization: token ${GITHUB_TOKEN}"
    curl -fsSL -H "${AUTH}" \
        "https://raw.githubusercontent.com/${GITHUB_REPO}/main/infra/control-plane/claude-md-template.md" \
        -o "/home/${OPERATOR_USER}/lab/CLAUDE.md"
    chown "${OPERATOR_USER}:${OPERATOR_USER}" "/home/${OPERATOR_USER}/lab/CLAUDE.md"
    echo "CLAUDE.md deployed from GitHub"
}

step_12_clone_repo() {
    if [[ -d "/home/${OPERATOR_USER}/lab/repo/.git" ]]; then
        echo "Repo already cloned, pulling latest"
        su - "$OPERATOR_USER" -c "cd ~/lab/repo && git pull"
    else
        su - "$OPERATOR_USER" -c "git clone https://github.com/${GITHUB_REPO}.git ~/lab/repo"
    fi
}

step_13_deploy_systemd() {
    # Deploy systemd units from GitHub (source of truth)
    local GH_RAW="https://raw.githubusercontent.com/${GITHUB_REPO}/main/infra/control-plane/systemd"
    local GH_API="https://api.github.com/repos/${GITHUB_REPO}/contents/infra/control-plane/systemd"
    local AUTH="Authorization: token ${GITHUB_TOKEN}"

    curl -fsSL -H "${AUTH}" "${GH_API}" | \
        jq -r '.[] | select(.type=="file" and (.name | endswith(".service"))) | .name' | while read -r fname; do
            curl -fsSL -H "${AUTH}" "${GH_RAW}/${fname}" -o "/etc/systemd/system/${fname}"
        done

    systemctl daemon-reload
    systemctl enable cloudflared ttyd ttyd-shell controlplane-api rclone-icloud
    echo "Systemd services deployed from GitHub"
}

step_14_start_services() {
    echo "Starting services..."
    systemctl start cloudflared
    systemctl start ttyd
    systemctl start ttyd-shell
    systemctl start controlplane-api
    if ! systemctl start rclone-icloud 2>/dev/null; then
        echo "WARN: rclone-icloud failed to start (expected: needs 2FA setup via SSM)"
    fi
    echo "Service status:"
    systemctl --no-pager status cloudflared ttyd ttyd-shell controlplane-api || true
}

step_15_health_check() {
    sleep 5
    echo "Checking FastAPI..."
    curl -sf http://localhost:8000/health | jq .
    echo "Checking cloudflared..."
    systemctl is-active cloudflared
    echo "Checking ttyd..."
    if curl -sf http://localhost:7681/ > /dev/null 2>&1; then
        echo "ttyd: OK"
    else
        sleep 3
        curl -sf http://localhost:7681/ > /dev/null && echo "ttyd: OK" || echo "WARN: ttyd not responding yet"
    fi
}

step_16_telegram_notify() {
    local instance_id instance_type az
    instance_id=$(curl -sf http://169.254.169.254/latest/meta-data/instance-id 2>/dev/null || echo "unknown")
    instance_type=$(curl -sf http://169.254.169.254/latest/meta-data/instance-type 2>/dev/null || echo "unknown")
    az=$(curl -sf http://169.254.169.254/latest/meta-data/placement/availability-zone 2>/dev/null || echo "unknown")

    local message="Control plane online
https://lab.bitbanshee.com
Instance: ${instance_id} (${instance_type})
AZ: ${az}"

    curl -sf "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
        -d chat_id="${TELEGRAM_CHAT_ID}" --data-urlencode text="${message}" \
        || echo "WARN: Telegram notification failed"
}

# ── Main ─────────────────────────────────────────────────────────────────────
echo "========================================"
echo "Control Plane Bootstrap"
echo "Started: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo "========================================"

BOOT_START=$(date +%s)

run_step  0 "System packages"         step_0_system_packages
run_step  1 "Swap file"               step_1_swap
run_step  2 "Fetch secrets"           step_2_fetch_secrets
run_step  3 "Configure environment"   step_3_configure_environment
run_step  4 "Node.js + Claude Code"   step_4_install_nodejs_claude
run_step  5 "Cloudflared"             step_5_install_cloudflared
run_step  6 "ttyd"                    step_6_install_ttyd
run_step  7 "rclone + iCloud"         step_7_install_rclone
run_step  8 "Python dependencies"     step_8_install_python_deps
run_step  9 "Operator directories"    step_9_setup_operator_dirs
run_step 10 "Deploy FastAPI app"      step_10_deploy_app
run_step 11 "CLAUDE.md"               step_11_write_claude_md
run_step 12 "Clone GitHub repo"       step_12_clone_repo
run_step 13 "Systemd services"        step_13_deploy_systemd
run_step 14 "Start services"          step_14_start_services
run_step 15 "Health check"            step_15_health_check
run_step 16 "Telegram notification"   step_16_telegram_notify

BOOT_END=$(date +%s)
echo ""
echo "========================================"
echo "Bootstrap complete in $((BOOT_END - BOOT_START))s"
echo "========================================"
update_status 16 "Complete" "complete"
