# Infrastructure & Operations

> This document covers the operational infrastructure for running the dual-process language model experiment on AWS spot instances. For research context, see [README.md](README.md).

## Table of Contents

- [AWS Architecture](#aws-architecture)
- [Spot Instance Resilience](#spot-instance-resilience)
- [Bootstrap](#bootstrap)
- [Checkpoint Management](#checkpoint-management)
- [Monitoring & Dashboards](#monitoring--dashboards)
- [Deployment](#deployment)
- [Cost Analysis](#cost-analysis)

## AWS Architecture

| Component | Details |
|-----------|---------|
| **Compute** | EC2 Spot Fleet (g5.2xlarge / g6.xlarge) — NVIDIA A10G or L4 GPUs |
| **Storage** | Instance NVMe for fast I/O, S3 for persistence (`s3://ml-lab-004507070771/dual-system-research-data/`) |
| **Secrets** | AWS Secrets Manager for W&B and HuggingFace tokens |
| **Tracking** | [Weights & Biases](https://wandb.ai) for real-time experiment logging |
| **CDN/TLS** | CloudFront (`EGWW28IMM7U2T`) → ACM certificate → `train.bitbanshee.com` |
| **DNS** | `train.bitbanshee.com` → CloudFront ALIAS; `origin.train.bitbanshee.com` → EC2 A record (bootstrap-managed) |
| **Failover** | Origin group: EC2 primary → S3 static fallback page on 500/502/503/504 |
| **Dashboard** | [train.bitbanshee.com](https://train.bitbanshee.com) — live web UI with training progress, GPU stats, loss curves, and cost tracking |

## Spot Instance Resilience

Training runs on spot instances with three layers of protection:

1. **S3 Sync Daemon** (`sync-checkpoints.sh`): Uploads checkpoints, logs, metrics, and preprocessed data to S3 every 60 seconds. The daemon runs under `set -uo pipefail` — if an individual `aws s3 sync` call fails (network issues, throttling), that cycle's output is logged but the daemon continues on the next 60-second interval. Training is not blocked by sync failures.
2. **SIGTERM Handler** (`SpotTerminationHandler` in `src/utils/s3_sync.py`): Catches the 2-minute termination warning and performs a final S3 sync before the instance dies.
3. **Checkpoint Resume** (`find_latest_checkpoint`): On startup, checks both local disk and S3 for the latest checkpoint, downloads if needed, and resumes training from that step.

## Bootstrap

`bootstrap.sh` handles full autonomous instance setup with real-time status tracking (written to `/tmp/bootstrap_status.json` for the dashboard to display). Pulled from S3 on every boot (`s3://ml-lab-004507070771/dual-system-research-data/deploy/bootstrap.sh`). Tested across multiple spot recovery cycles with zero manual intervention.

| Step | Action | Notes |
|------|--------|-------|
| 0 | NVMe ephemeral storage | Create data directories on fast local disk |
| 1 | Fetch secrets | W&B, HuggingFace, dashboard tokens from Secrets Manager |
| 2 | Configure environment | `.bashrc` env vars, git credentials |
| 3 | Pull latest code | `git pull --ff-only` |
| 4 | Restore artifacts from S3 | Checkpoints, logs, eval metrics, benchmarks (**bottleneck: ~3 min** — downloads all checkpoints at ~1.4 GB each, plus logs, eval metrics, and benchmarks) |
| 5 | Sync preprocessed data | Tokenized training data from S3 |
| 6 | Fix file ownership | S3 restores as root |
| 7 | Update CloudFront DNS | `origin.train.bitbanshee.com` A record → instance IP |
| 8 | Start sync daemon | `sync-checkpoints.sh` (60s interval) |
| 9 | Install nginx | apt install (if missing) |
| 10 | Configure nginx | HTTP-only reverse proxy (CloudFront handles TLS) |
| 11 | Install Flask | pip install (if missing) |
| 12 | Start web dashboard | Flask on :5000 |
| 13 | Setup spot price updater | Initial run + cron every 5 min |
| 14 | Setup cost tracker | `cost-tracker.sh` — initial run + cron |
| 15 | Launch training | tmux session, auto-resumes from latest checkpoint |

## Checkpoint Management

- **Save frequency**: Every 1,000 training steps
- **Local retention**: Last 3 checkpoints (automatic cleanup)
- **S3 retention**: All checkpoints preserved
- **Format**: PyTorch `.pt` files containing model state, optimizer state, scheduler state, step counter, and RNG states
- **File size**: ~1.4 GB per checkpoint (GPT-2 Small; dominated by optimizer state)
- **Resume logic**: On startup, compares local and S3 checkpoints, downloads the latest if S3 is ahead

## Monitoring & Dashboards

Three monitoring interfaces share the same on-disk data sources but serve different use cases.

### Data Flow

```
joint_trainer.py
  ├─ wandb output.log ──────── step lines (ar_loss, diff_loss, conf_acc, lr, time)
  │                             [eval] lines (ar_ppl, diff_loss, s1_tok_acc, conf_acc, conf_ece, conf_auroc)
  ├─ eval_metrics/*.json ────── one JSON per eval checkpoint
  ├─ checkpoints/*.pt ───────── model + optimizer state
  └─ configs/tiny.yaml ──────── training hyperparameters

/tmp/spot_price.json ────────── spot pricing (written by cron via update-spot-price.sh)
/tmp/bootstrap_status.json ──── bootstrap progress (written by bootstrap.sh)
EC2 IMDS v2 ─────────────────── instance type, lifecycle, AZ, boot time
nvidia-smi ──────────────────── GPU util, VRAM, temp, power
```

### web_dashboard.py — Live Web Dashboard

![ML Lab Dashboard](static/ml-lab-dashboard.png)

Single-file Flask application (1,800 lines) serving an inline HTML/CSS/JS dashboard at [train.bitbanshee.com](https://train.bitbanshee.com). Designed for remote monitoring over CloudFront.

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Server-Sent Events (SSE) at `/stream` (10s interval) |
| Frontend | Vanilla JS, Chart.js (loss curves + eval metrics), inline CSS |
| Caching | Per-key TTL cache (2–60s) to avoid re-parsing on every SSE push |
| Proxy | nginx (HTTP, port 80) → CloudFront (TLS termination) → `train.bitbanshee.com` |

**Key features:**
- **Live metrics cards** (6 tiles: AR Loss, Diff Loss, Conf Acc, AUROC, S1 Acc, LR) with RAG color coding and sparklines
- **Loss curves chart** — AR loss + diffusion loss over training steps, auto-refreshes on new data
- **Eval metrics chart** — S1 token accuracy, AUROC, AR perplexity; filtered to current run only
- **GPU gauges** — utilization, VRAM, temperature, power with color thresholds
- **Spot cost tracking** — live spot pricing, accumulated cost, projected run total
- **Bootstrap progress panel** — step-by-step instance boot status (auto-hides when complete)
- **Infrastructure status** — trainer/sync daemon health, checkpoint list, next milestones

**API endpoints:**

| Endpoint | Description |
|----------|------------|
| `GET /api/status` | Full status payload (training, eval, GPU, cost, infra, bootstrap) |
| `GET /api/history` | Training step data for loss chart |
| `GET /api/eval/history` | Merged eval JSONs + log-parsed eval lines |
| `GET /stream` | SSE stream — pushes `/api/status` every 10s |
| `POST /api/spot-price` | Accepts spot price data from external updater (token-auth) |

### monitor.sh — Terminal Dashboard

![Terminal Dashboard](static/terminal-dashboard.png)

Bash script (430 lines) rendering a full-screen ANSI terminal dashboard. Designed for SSH sessions on the GPU instance.

```bash
./monitor.sh        # 15s refresh (default)
./monitor.sh 5      # 5s refresh
```

### dashboard.py — Curses Job Manager TUI

Python curses application (880 lines) for interactive job management. Launches training, smoke tests, or pytest from a menu and monitors the running process with live output, GPU stats, and parsed metrics.

```bash
python dashboard.py              # Interactive menu
python dashboard.py --job tiny   # Launch training directly
python dashboard.py --job smoke  # Launch smoke test
python dashboard.py --job test   # Launch pytest
```

### Comparison

| Feature | web_dashboard.py | monitor.sh | dashboard.py |
|---------|-----------------|------------|-------------|
| Access | Browser (remote) | SSH terminal | SSH terminal |
| Charts | Chart.js (loss + eval) | Sparklines (ANSI) | — |
| RAG indicators | Color-coded metric cards | Color-coded gauges | — |
| Cost tracking | Full (on-demand + spot) | Full | — |
| Bootstrap status | Progress panel | — | — |
| Job control | View only | View only | Launch + monitor |
| Dependencies | Flask, nginx, CloudFront | bash, bc, python3 | Python curses |

## Deployment

### AMI Snapshots

The training environment is baked into an AMI to avoid lengthy setup on each spot instance launch:
- AMI: `ami-0ab66bc7f8ec4fbd1` (launch template `lt-06e111b12bd85396f`, v17)
- Pre-installed: Python 3.12, PyTorch 2.6, CUDA 12.8, full ML stack
- Fleet ID: `fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a` (set capacity 0/1 to stop/start)

### Quick Start (Instance Management)

```bash
# Start the fleet (launches a spot instance)
aws ec2 modify-spot-fleet-request --spot-fleet-request-id fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a --target-capacity 1

# Stop the fleet
aws ec2 modify-spot-fleet-request --spot-fleet-request-id fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a --target-capacity 0

# SSH to instance
ssh -i gpu-key.pem ubuntu@origin.train.bitbanshee.com
```

## Cost Analysis

### Spot Pricing

Spot pricing varies by instance type and availability zone. The `update-spot-price.sh` script monitors current prices via cron (every 5 minutes) and feeds data to the dashboard.

| Instance | GPU | On-Demand | Spot (typical) | Savings |
|----------|-----|-----------|----------------|---------|
| g5.2xlarge | A10G (24GB) | $1.212/hr | ~$0.43/hr | ~65% |
| g6.xlarge | L4 (24GB) | $0.805/hr | ~$0.30/hr | ~63% |

### Projected Training Cost

**Pure compute estimate** (uninterrupted):
- 50,000 steps at ~4.7 steps/sec = ~3 hours of GPU time (excluding eval pauses)
- g5.2xlarge spot: ~$1.30 per complete run
- g6.xlarge spot: ~$0.90 per complete run

**Actual wall time** is significantly longer due to spot interruptions, bootstrap recovery (~5 min per cycle), and instance availability gaps. The current training run (~12,000 steps) has spanned 4 spot allocations over several days. A reliable cost-per-run estimate requires a complete uninterrupted run.

S3 storage: negligible (~$0.02/month for checkpoints and logs)
