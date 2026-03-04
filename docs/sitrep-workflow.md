# Sitrep Workflow

How the situation report pipeline works — from generation to delivery.

## Overview

The sitrep pipeline automatically generates a human-readable situation report (`sitrep.md`) every 30 minutes during training, commits it to git, syncs it to S3, and serves it through a web dashboard. The pipeline has two delivery paths: Flask on EC2 (primary) and Lambda via API Gateway (fallback), unified behind CloudFront.

## Architecture

```
                        cron (every 30 min)
                              │
                        auto_sitrep.py
                         │          │
             fetches     │          │  writes
         /api/status     │          │
          (Flask)        │          ▼
                         │     sitrep.md ──── git commit+push ──→ GitHub
                         │          │
                         │          │  (every 60s)
                         │     sync-checkpoints.sh
                         │          │
                         │          ▼
                         │     S3 bucket
                         │     ml-lab-004507070771/
                         │     dual-system-research-data/
                         │     sitrep.md
                         │          │
                         ▼          ▼
             Flask /api/sitrep   Lambda /api/sitrep
             (reads disk)        (reads S3)
                    │                  │
                    ▼                  ▼
              EC2 origin        API Gateway origin
              (primary)         (failover)
                    │                  │
                    └──── CloudFront ──┘
                              │
                              ▼
                    train.bitbanshee.com
                    (dashboard modal)
```

## Components

### 1. auto_sitrep.py

**Purpose:** Generate the sitrep markdown and commit it to the repo.

**Schedule:** Cron, every 30 minutes.

**What it does:**

1. Fetches live training status from `http://localhost:5000/api/status` (Flask dashboard)
2. Loads eval metric JSONs from `/opt/dlami/nvme/ml-lab/eval_metrics/eval_step_*.json`
3. Loads the cost ledger from `/opt/dlami/nvme/ml-lab/cost/cost_ledger.json`
4. Maintains a cumulative eval history in `/tmp/auto-sitrep-eval-history.json` (survives across cron runs but not reboots)
5. Generates `sitrep.md` with: progress, GPU stats, rate/ETA, cost, eval trajectory table, target status, trends, spot instance history
6. Writes to `/home/ubuntu/KahnemanHybridExperiment/sitrep.md`
7. Runs `git add sitrep.md && git commit && git push` (skips if no changes)

**Key paths:**

| Path | Purpose |
|------|---------|
| `/home/ubuntu/KahnemanHybridExperiment/sitrep.md` | Output file |
| `/opt/dlami/nvme/ml-lab/eval_metrics/` | Eval checkpoint JSONs |
| `/opt/dlami/nvme/ml-lab/cost/cost_ledger.json` | Cumulative cost data |
| `/tmp/auto-sitrep-eval-history.json` | Eval history across cron runs |

### 2. sync-checkpoints.sh

**Purpose:** Sync training artifacts (including `sitrep.md`) to S3 every 60 seconds.

**Runs as:** Background daemon (started by bootstrap).

**Sitrep-relevant behavior:**

- Copies `/home/ubuntu/KahnemanHybridExperiment/sitrep.md` to `s3://ml-lab-004507070771/dual-system-research-data/sitrep.md`
- This makes the sitrep available to the Lambda fallback
- Also syncs: checkpoints, eval_metrics, benchmarks, logs, cost, wandb
- Exports experiment CSVs (eval_metrics.csv, training_steps.csv) and auto-commits them to git
- Handles SIGTERM gracefully with a final sync

### 3. Flask /api/sitrep (EC2)

**Source:** `web_dashboard.py`, route `/api/sitrep`

**Behavior:**

- Reads `sitrep.md` from disk at `/home/ubuntu/KahnemanHybridExperiment/sitrep.md`
- Returns JSON: `{"content": "<markdown>", "modified": "<ISO timestamp>"}`
- If the file doesn't exist, returns `{"content": "_No sitrep available yet._", "modified": null}`
- `modified` is derived from the file's mtime on disk

**Only available when EC2 is running.** CloudFront routes to this as the primary origin.

### 4. Lambda /api/sitrep (Always-on fallback)

**Source:** `infra/lambda/dashboard_api.py`, handler function `_handle_sitrep()`

**Behavior:**

- Reads `sitrep.md` from `s3://ml-lab-004507070771/dual-system-research-data/sitrep.md`
- Returns the same JSON shape: `{"content": "<markdown>", "modified": "<ISO timestamp>"}`
- `modified` is the S3 object's `LastModified` timestamp
- Caches S3 reads for 30 seconds (Lambda container reuse)
- Returns empty content if the S3 object doesn't exist

**Always available**, even when EC2 is offline. CloudFront fails over to this origin when EC2 returns 5xx or times out (~30s failover delay).

**Infrastructure:**
- Lambda: `ml-lab-dashboard-api` (Python 3.12, 128MB, 10s timeout)
- API Gateway: HTTP API `poemtdqibf` (`https://poemtdqibf.execute-api.us-east-1.amazonaws.com`)
- CloudFront origin group: `api-with-lambda-fallback` handles `/api/*` and `/stream`

## Timezone Bug (Known Issue)

In `auto_sitrep.py`:

```python
ET = timezone(timedelta(hours=-4))
```

This hardcodes UTC-4 (EDT), but Eastern Time switches between EDT (UTC-4) and EST (UTC-5) depending on daylight saving time. DST starts March 8, 2026 — so between November and March, the header timestamp is **off by 1 hour**.

**Impact:** The sitrep header shows times like "3:30 PM ET / 19:30 UTC" but during EST months, it should show "2:30 PM ET / 19:30 UTC" (the UTC time is always correct).

**Fix:**

```python
# Before (broken)
from datetime import timezone, timedelta
ET = timezone(timedelta(hours=-4))

# After (correct)
from zoneinfo import ZoneInfo
ET = ZoneInfo("America/New_York")
```

`ZoneInfo` is in the standard library since Python 3.9 and handles DST transitions automatically.

## Failure Modes

| Failure | Sitrep impact | Dashboard impact |
|---------|---------------|------------------|
| **EC2 down** | `auto_sitrep.py` stops running; sitrep goes stale | Lambda serves the last-synced version from S3; dashboard shows offline banner |
| **auto_sitrep.py crash** | Sitrep stops updating | Dashboard still works — Flask serves stale `sitrep.md` from disk, Lambda serves stale copy from S3 |
| **sync-checkpoints.sh failure** | S3 copy goes stale | Lambda serves stale data; Flask still reads from disk normally |
| **S3 unreachable** | No effect on generation | Lambda returns empty; Flask unaffected |
| **Flask down, EC2 up** | `auto_sitrep.py` fails (can't fetch `/api/status`); exits with error | CloudFront fails over to Lambda for `/api/*` |
| **Git push fails** | Sitrep still written to disk and synced to S3 | No effect on dashboard delivery |

**Staleness chain:** auto_sitrep.py writes every 30 min → sync daemon copies to S3 within 60s → Lambda caches S3 reads for 30s. Maximum staleness when EC2 goes down: ~32 minutes (worst case: EC2 dies right before the next cron run, the last-written sitrep was from 30 min ago, plus 60s sync delay, plus 30s Lambda cache).

## Manual Operations

When the EC2 instance is offline (fleet capacity = 0), automation doesn't run. To manually update the sitrep:

### Option 1: Edit on GitHub directly

1. Go to `https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment/blob/main/sitrep.md`
2. Edit the file in GitHub's web editor
3. Commit the change

Note: This updates the git repo but **not** the S3 copy. The dashboard (via Lambda) will still show the old version until you also update S3.

### Option 2: Update S3 directly

```bash
# Write or edit sitrep locally
vim /tmp/sitrep.md

# Push to S3 (makes it visible on the dashboard via Lambda)
aws s3 cp /tmp/sitrep.md \
  s3://ml-lab-004507070771/dual-system-research-data/sitrep.md \
  --profile ml-lab

# Optionally also push to GitHub
gh api repos/BITBANSHEE-C137/KahnemanHybridExperiment/contents/sitrep.md \
  -X PUT \
  -f message="Manual sitrep update" \
  -f content="$(base64 -w0 /tmp/sitrep.md)" \
  -f sha="$(gh api repos/BITBANSHEE-C137/KahnemanHybridExperiment/contents/sitrep.md --jq '.sha')"
```

### Option 3: SSH to EC2 and run manually

If the instance is running but the cron job isn't:

```bash
ssh -i gpu-key.pem ubuntu@origin.train.bitbanshee.com
cd /home/ubuntu/KahnemanHybridExperiment
python3 auto_sitrep.py
```
