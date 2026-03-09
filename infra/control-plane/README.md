# ML Lab Control Plane

Persistent Claude Code operator instance, accessible from any browser (including iPhone Safari) via Cloudflare tunnel.

## Architecture

```
Browser / iPhone Safari
      |
Cloudflare Access (Zero Trust, email OTP)
      |
Cloudflare Tunnel (outbound-only from EC2)
      |
EC2 t3.small (on-demand, same VPC as GPU fleet)
  +-- cloudflared (systemd)     -> tunnel daemon
  +-- ttyd :7681 (localhost)    -> WebSocket terminal
  |     \__ tmux "cc-control"   -> Claude Code
  +-- FastAPI :8000             -> elevation API + web UI
  +-- rclone FUSE mount         -> iCloud Drive (read-only)
```

## Prerequisites (Manual Steps)

Before running any scripts:

1. Create Cloudflare account and API token (Tunnel Edit + Access Edit permissions)
2. Create Cloudflare Access application for `lab.bitbanshee.com` with email OTP
3. Generate iCloud app-specific password at appleid.apple.com
4. Create Cloudflare tunnel: `cloudflared tunnel create bitbanshee-lab-control`
5. Store secrets in AWS Secrets Manager:
   - `ml-lab/cloudflare-tunnel-creds` — tunnel credentials JSON
   - `ml-lab/icloud-apple-id` — Apple ID email
   - `ml-lab/icloud-app-password` — app-specific password
   - `ml-lab/gpu-ssh-key` — SSH key for GPU instances
   - `ml-lab/cf-policy-aud` — Cloudflare Access policy AUD tag

## Deployment

```bash
# 1. Create IAM roles
./iam-setup.sh

# 2. Upload app files to S3
aws s3 sync app/ s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane/app/
aws s3 cp bootstrap.sh s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane-bootstrap.sh
aws s3 sync systemd/ s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane/systemd/
aws s3 cp claude-md-template.md s3://ml-lab-004507070771/dual-system-research-data/deploy/control-plane/claude-md-template.md

# 3. Launch EC2 instance
./launch.sh

# 4. Set up DNS (get tunnel UUID from Cloudflare)
./dns-setup.sh <tunnel-uuid>
```

## Elevation System

Claude Code operates with read-only permissions by default. When it needs write access:

1. Claude Code sends `POST /api/elevation/request` with action + justification
2. Human receives Telegram notification + sees request in web UI
3. Human clicks Approve (validated via Cloudflare Access JWT — cannot be forged)
4. Claude Code gets temporary AWS credentials (1 hour max)
5. Credentials auto-expire and are revoked

**Security**: Approval requires a valid Cloudflare-signed JWT, which only exists in requests through the tunnel. Claude Code's local `curl` requests cannot forge this token.

## Services

| Service | Port | Description |
|---|---|---|
| cloudflared | — | Cloudflare tunnel daemon |
| ttyd | 7681 | Terminal WebSocket server |
| controlplane-api | 8000 | FastAPI backend |
| rclone-icloud | — | iCloud FUSE mount |
| cc-tmux | — | tmux session manager |

## Cost

~$18.30/month (t3.small on-demand + 20GB EBS + data transfer + Secrets Manager)

## Troubleshooting

```bash
# Check service status
systemctl status cloudflared ttyd controlplane-api cc-tmux rclone-icloud

# View bootstrap log
cat /var/log/control-plane-bootstrap.log

# View bootstrap status
cat /var/log/control-plane-status.json

# Restart all services
systemctl restart cloudflared ttyd controlplane-api

# Check elevation database
sqlite3 /opt/control-plane/elevation.db "SELECT * FROM elevations ORDER BY requested_at DESC LIMIT 5;"

# Manual iCloud setup (first time only)
sudo -u claude-operator rclone config reconnect icloud:
```
