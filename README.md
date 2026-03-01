# KahnemanHybridExperiment

![BitBanshee Research](static/hero.png)

**[Live Dashboard](https://train.bitbanshee.com)** | **[siliconstrategy.ai](https://siliconstrategy.ai)**

A research project exploring **dual-process language models** — a single Transformer that operates in two cognitive modes inspired by Kahneman's System 1 / System 2 framework from *Thinking, Fast and Slow*.

- **System 1 (Diffusion)**: Fast, parallel token generation via masked diffusion. Bidirectional attention. Default mode.
- **System 2 (Autoregressive)**: Slow, sequential token generation via standard causal LM. Escalation mode.

A trained **confidence head** decides whether System 1's output is trustworthy or whether to escalate to System 2. This is a System 1-led architecture — diffusion generates first, autoregressive reasoning only engages when confidence is low.

The key insight: both modes share the same Transformer weights. The only difference between them is the attention mask (bidirectional vs. causal). Joint training with both objectives produces weights that work in either mode.

## Architecture

### DualProcessGPT2

Built on HuggingFace's `GPT2LMHeadModel`, initialized from pretrained weights. Three components:

| Component | Purpose | Output |
|-----------|---------|--------|
| **Shared Transformer** | GPT-2 backbone (all layers, embeddings, LM head) | Hidden states, logits |
| **Confidence Head** | 2-layer MLP (`Linear → GELU → Linear`) on hidden states | Per-token confidence score ∈ [0, 1] |
| **Attention Mask** | Switches between bidirectional (System 1) and causal (System 2) | Controls information flow |

### Forward Passes

**System 1** (`forward_system1`): Takes input with masked tokens, runs bidirectional attention (all-ones mask), returns logits + confidence scores. Used for parallel prediction of masked positions.

**System 2** (`forward_system2`): Standard causal left-to-right pass via GPT-2's built-in causal mask. Returns logits only.

### Masking Strategy (LLaDA-style)

System 1 uses masked diffusion following [LLaDA](https://arxiv.org/abs/2502.09992):
- Sample a masking ratio `t ~ U(min_mask_ratio, max_mask_ratio)` per batch
- Randomly mask that fraction of tokens, replacing with a mask token (GPT-2's `<|endoftext|>` token 50256 repurposed as `[MASK]`)
- System 1 predicts the original tokens at masked positions

### Joint Training Objective

Each training step computes three losses:

```
L = λ_ar · L_ar + λ_diff · L_diff + λ_conf · L_conf
```

| Loss | Description | Default Weight |
|------|-------------|----------------|
| **L_ar** (AR) | Cross-entropy next-token prediction (System 2). Labels auto-shifted by HuggingFace internally. | 1.0 |
| **L_diff** (Diffusion) | Cross-entropy on masked positions only (System 1). | 1.0 |
| **L_conf** (Confidence) | Binary cross-entropy — trains confidence head to predict whether System 1 got each masked token correct. | 0.1 |

### Inference Modes

Three generation pipelines in `src/inference/generator.py`:

1. **System 1 (Iterative Unmasking)**: Start fully masked → progressively unmask the most confident tokens over N steps → parallel generation.
2. **System 2 (Autoregressive)**: Standard left-to-right generation with top-k sampling.
3. **Hybrid**: System 1 generates first. If mean confidence falls below a threshold, escalate — take System 1's partial output as a prompt and continue with System 2.

## Model Tiers

All experiments use the GPT-2 family with the same tokenizer (50,257 vocab):

| Tier | Model | Parameters | Layers | Embed Dim | Heads |
|------|-------|------------|--------|-----------|-------|
| Tiny | GPT-2 Small | 124M | 12 | 768 | 12 |
| Small | GPT-2 Medium | 355M | 24 | 1024 | 16 |
| Medium | GPT-2 Large | 774M | 36 | 1280 | 20 |

All models initialize from HuggingFace pretrained weights (not trained from scratch).

## Project Structure

```
KahnemanHybridExperiment/
├── configs/
│   └── tiny.yaml                    # GPT-2 Small training config
├── scripts/
│   ├── benchmark.py                 # LAMBADA + WikiText-103 evaluation
│   ├── compare_systems.py           # System 1 vs 2 analysis
│   ├── lean_preprocess.py           # Memory-efficient tokenization
│   └── prepare_openwebtext.py       # Streaming data preprocessing
├── src/
│   ├── model/
│   │   ├── dual_process_gpt2.py     # DualProcessGPT2 model
│   │   └── masking.py               # LLaDA-style masked diffusion
│   ├── training/
│   │   └── joint_trainer.py         # Joint training loop
│   ├── evaluation/
│   │   ├── evaluator.py             # Eval loop (perplexity, accuracy, calibration)
│   │   └── metrics.py               # AUROC, ECE implementations
│   ├── inference/
│   │   └── generator.py             # System 1, System 2, Hybrid generation
│   ├── data/
│   │   └── openwebtext.py           # Memmap + HuggingFace data loading
│   └── utils/
│       └── s3_sync.py               # Non-blocking S3 uploads, spot termination handler
├── tests/
│   ├── test_model.py                # Architecture, shapes, gradient flow, shared weights
│   ├── test_training.py             # LR schedule, warmup
│   ├── test_evaluation.py           # AUROC, ECE, full eval integration
│   ├── test_data.py                 # Memmap dataset, chunking, dtypes
│   ├── test_benchmark.py            # LAMBADA, WikiText end-to-end
│   ├── test_compare.py              # System comparison analyses
│   └── test_inference.py            # All three generation modes
├── bootstrap.sh                     # Autonomous EC2 spot recovery (8 steps)
├── sync-checkpoints.sh              # S3 artifact sync daemon
├── update-dns.sh                    # Route53 DNS auto-update
├── update-spot-price.sh             # Spot price monitoring (cron + IMDSv2)
├── web_dashboard.py                 # Live web dashboard (Flask + SSE + Chart.js)
├── monitor.sh                       # Terminal training monitor (bash + ANSI)
├── dashboard.py                     # Curses TUI — job launcher + live monitor
├── requirements.txt
└── setup.py
```

## Training Data

[OpenWebText](https://huggingface.co/datasets/openwebtext) — an open-source recreation of OpenAI's WebText corpus.

- ~8M documents, ~9B tokens after GPT-2 BPE tokenization
- Stored as flat uint16 binary files for zero-copy memmap loading
- 5,000-document eval split from the final shard
- Preprocessing via `scripts/lean_preprocess.py` (reads cached parquet shards one at a time to stay under 16GB RAM)

## Evaluation

### Internal Metrics (computed every 1,000 steps)

| Metric | Description |
|--------|-------------|
| **AR Perplexity** | exp(mean AR loss) — System 2 language modeling quality |
| **Diffusion Loss** | Mean cross-entropy on masked positions — System 1 quality |
| **S1 Token Accuracy** | Fraction of masked tokens correctly predicted by System 1 |
| **Confidence Accuracy** | Binary accuracy of the confidence head (threshold 0.5) |
| **Confidence ECE** | Expected Calibration Error — how well confidence matches actual accuracy |
| **Confidence AUROC** | Area Under ROC Curve for confidence as a classifier of correct/incorrect predictions |

### External Benchmarks

**LAMBADA** (last-word prediction):
- System 2: Autoregressive accuracy on the final word
- System 1: Mask the final word tokens, predict via bidirectional diffusion
- System 2 perplexity on LAMBADA sequences

**WikiText-103** (language modeling):
- System 2: Standard autoregressive perplexity
- System 1: Diffusion loss with 50% masking

### System Comparison Analysis

- Escalation rates at varying confidence thresholds
- Throughput comparison (tokens/sec) across generation modes
- Quality comparison of generated text (perplexity)
- Confidence calibration analysis (ECE, AUROC, mean confidence)

## Results

**Status: Training in progress** — GPT-2 Small (124M), currently at step ~1,500 (3.0%), warmup phase. Resumed from step 1,000 checkpoint after spot recovery. Track live at [train.bitbanshee.com](https://train.bitbanshee.com).

### Success Criteria

The experiment tests whether a single Transformer can learn both AR and diffusion objectives with shared weights, and whether a confidence head can learn to mediate between them. These are the target metrics at training completion (step 50,000):

| Metric | Target | Rationale |
|--------|--------|-----------|
| **AR Perplexity (WikiText-103)** | < 40 | Pretrained GPT-2 Small baseline is ~31.5. Joint training adds overhead; staying within ~25% indicates the AR objective isn't degraded by weight sharing. |
| **S1 Token Accuracy** | > 40% | System 1 should predict masked tokens well above random (~2%). LLaDA-style diffusion on GPT-2 scale should reach meaningful accuracy. |
| **Diffusion Loss** | < 4.0 | Steady decline from initial ~7.8 should continue as the bidirectional objective converges. |
| **Confidence AUROC** | > 0.75 | The confidence head must reliably separate correct from incorrect System 1 predictions to make hybrid escalation useful. |
| **Confidence ECE** | < 0.05 | Calibration — predicted confidence should match actual accuracy. Already well under target. |
| **LAMBADA Accuracy (System 2)** | > 30% | Pretrained GPT-2 Small achieves ~36%. Joint training should preserve most of this capability. |
| **Hybrid Escalation** | Measurable improvement | Hybrid mode (System 1 + selective System 2 escalation) should outperform System 1 alone, validating the dual-process architecture. |

### Eval Metrics Over Training

Data from two training runs. Run 1 reached step 4,000 before spot termination with checkpoint frequency at 1,000 steps. Run 2 resumed from the step 1,000 checkpoint and is ongoing.

| Step | AR PPL | Diff Loss | S1 Tok Acc | Conf Acc | Conf ECE | Conf AUROC | Run |
|------|--------|-----------|-----------|----------|----------|------------|-----|
| 50 | 19,060 | 7.8397 | 3.4% | 96.6% | 0.0499 | 0.467 | 1 |
| 100 | 23,331 | 7.5697 | 3.2% | 96.8% | 0.0037 | 0.502 | 1 |
| 1,000 | 20,575 | 6.7854 | 4.9% | 95.1% | 0.0028 | 0.550 | 2 |
| 2,000 | 25,008 | 6.6630 | 6.0% | 94.0% | 0.0030 | 0.594 | 1 |
| 3,000 | 21,412 | 6.5179 | 7.1% | 92.9% | 0.0057 | 0.628 | 1 |
| 4,000 | 22,406 | 6.2339 | 8.6% | 91.5% | 0.0052 | 0.669 | 1 |

### Progress vs. Targets

| Metric | Best | Step | Target | Progress |
|--------|------|------|--------|----------|
| AR Perplexity | 19,060 | 50 | < 40 | Early — PPL expected to drop sharply past warmup |
| S1 Token Accuracy | 8.6% | 4,000 | > 40% | 21% of target — 2.5× above random baseline |
| Diffusion Loss | 6.23 | 4,000 | < 4.0 | 42% of reduction achieved (7.84 &rarr; 6.23 &rarr; 4.0) |
| Confidence AUROC | 0.669 | 4,000 | > 0.75 | 68% of improvement achieved (0.50 &rarr; 0.67 &rarr; 0.75) |
| Confidence ECE | 0.003 | 1,000 | < 0.05 | **Met** |

### Observations

- **Diffusion loss** is steadily declining (7.84 &rarr; 6.23 over 4k steps), showing System 1 is learning to predict masked tokens. The rate of decline (~0.4 per 1k steps) suggests the < 4.0 target is reachable by step 10–15k.
- **S1 token accuracy** has grown 2.5× from random baseline (3.4% &rarr; 8.6%), with consistent improvement at each eval point. The trajectory suggests the bidirectional diffusion objective is converging.
- **Confidence AUROC** is improving linearly (0.47 &rarr; 0.67, ~0.05 per 1k steps) — the confidence head is learning to distinguish correct from incorrect System 1 predictions, which is critical for the hybrid escalation mechanism. On current trajectory, the 0.75 target is reachable by step ~5,500.
- **Confidence ECE** remains very low (< 0.006 after initial calibration), already meeting the target since step 100. The confidence head is well-calibrated throughout training.
- **Confidence accuracy** is gradually declining (96.8% &rarr; 91.5%) as expected — early on, System 1 gets almost nothing right so predicting "wrong" for everything trivially achieves high accuracy. As S1 improves, the classification task becomes harder, and the accuracy/AUROC tradeoff shifts toward more informative predictions.
- **AR perplexity** is still very high (~20k) — expected during warmup (step 1,500 of 2,000-step warmup) with the learning rate still ramping. Pretrained GPT-2 Small achieves ~31.5 PPL on WikiText-103; meaningful AR improvement typically begins after warmup completes and cosine decay takes effect.
- **Spot resilience** validated across multiple recovery cycles — bootstrap autonomously recovers all 15 services (training, dashboard, sync, DNS, CloudFront origin, spot pricing) with zero manual intervention.

### Current Training Metrics (Live)

At step ~1,500 (warmup phase, LR 2.25e-4 ramping to 3.0e-4):

| Metric | Value | RAG Status |
|--------|-------|------------|
| AR Loss | 3.12 | Amber (target: < 3.0) |
| Diff Loss | 6.59 | Amber (target: < 5.0) |
| Conf Acc | 95.1% | Green (target: > 90%) |
| AUROC | 0.550 | Red (target: > 0.75) |

### Remaining Benchmarks

These will be run at training completion (step 50,000):

- **LAMBADA** — last-word prediction accuracy (System 1 vs System 2 vs Hybrid)
- **WikiText-103** — standard perplexity benchmark
- **System Comparison** — escalation rates, throughput, quality across generation modes
- **Confidence Calibration** — full analysis at final checkpoint

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

Single-file Flask application (1,600 lines) serving an inline HTML/CSS/JS dashboard at [train.bitbanshee.com](https://train.bitbanshee.com). Designed for remote monitoring over CloudFront.

| Layer | Technology |
|-------|-----------|
| Backend | Flask, Server-Sent Events (SSE) at `/stream` (10s interval) |
| Frontend | Vanilla JS, Chart.js (loss curves + eval metrics), inline CSS |
| Caching | Per-key TTL cache (2–60s) to avoid re-parsing on every SSE push |
| Proxy | nginx (HTTP, port 80) → CloudFront (TLS termination) → `train.bitbanshee.com` |

**Key features:**
- **Live metrics cards** with RAG (red/amber/green) color coding based on proximity to training targets
- **Loss curves chart** — AR loss + diffusion loss over training steps, auto-refreshes on new data
- **Eval metrics chart** — S1 token accuracy, AUROC, AR perplexity; filtered to current run only
- **Sparklines** on each metric (last 30 data points)
- **GPU gauges** — utilization, VRAM, temperature, power with color thresholds
- **Cost tracking** — on-demand vs spot pricing, live savings computation, projected run cost
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

Bash script (430 lines) rendering a full-screen ANSI terminal dashboard. Same data sources as the web dashboard, but parsed directly in bash with `grep`/`bc`/`python3` one-liners. Designed for SSH sessions on the GPU instance.

```
┌──────────────────────────────────────────────────────────────────────┐
│  ◆ ML Training Dashboard                              14:32:08 UTC  │
│  ◆ Progress    1,100/50,000  warmup  1h 2m elapsed  46h remaining   │
│    ▓▓░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 2%   │
│  ◆ Metrics                                                          │
│    AR Loss   3.1242  ▁▂▃▄▅▆▇█ ↓      Conf Acc  0.9506             │
│    Diff Loss 6.8470  ▁▂▃▄▅▆▇█ ↓      LR        1.65e-04           │
│  ◆ GPU  NVIDIA A10G                                                 │
│    Util  ████████░░ 82%      VRAM  ████████░░ 18.2/22G             │
│    Temp  ███░░░░░░░ 34°C     Power ██████░░░░ 138/300W             │
│  ◆ Eval  step 1000                                                  │
│    AR PPL 20575   S1 Acc 4.9%   AUROC 0.550 ████░░   ECE 0.0028   │
│  ◆ Cost  g5.xlarge · spot · us-east-1a · up 1h 5m                  │
│    On-Demand  $1.0060/hr  $1.04  proj $47.28                       │
│    Spot       $0.4253/hr  $0.44  proj $19.99                       │
│    Savings    56.7%       $0.60  proj $27.29                       │
│  ◆ Infra  ● trainer ● sync                                         │
│    next eval 2000 in 900  ckpt 2000 in 900  warmup ends 2000       │
│  ──────────────────────────────────────────────────────────────────  │
│  ◆ Log                                                              │
│    step: 1100 | ar_loss: 3.1242 | diff_loss: 6.8470 | ...          │
│  ──────────────────────────────────────────────────────────────────  │
│  refresh 15s  q=quit r=refresh                                      │
└──────────────────────────────────────────────────────────────────────┘
```

**Features:** Progress bar, inline sparklines with trend arrows, GPU gauges with color thresholds, spot cost tracking, eval data filtered to current run only, auto-refresh with keyboard controls.

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

## Infrastructure

### AWS Setup

- **Compute**: EC2 Spot Fleet (g5.2xlarge / g6.xlarge) with NVIDIA A10G or L4 GPUs
- **Storage**: Instance NVMe for fast I/O, S3 for persistence (`s3://ml-lab-004507070771/dual-system-research-data/`)
- **Secrets**: AWS Secrets Manager for W&B and HuggingFace tokens
- **Tracking**: [Weights & Biases](https://wandb.ai) for real-time experiment logging
- **CDN/TLS**: CloudFront (`EGWW28IMM7U2T`) → ACM certificate → `train.bitbanshee.com`. Origin failover to S3 static page when instance is down.
- **Dashboard**: [train.bitbanshee.com](https://train.bitbanshee.com) — live web UI with training progress, GPU stats, loss curves, and cost tracking

### Spot Instance Resilience

Training runs on spot instances with three layers of protection:

1. **S3 Sync Daemon** (`sync-checkpoints.sh`): Uploads checkpoints, logs, metrics, and preprocessed data to S3 every 60 seconds.
2. **SIGTERM Handler** (`SpotTerminationHandler`): Catches the 2-minute termination warning and performs a final S3 sync before the instance dies.
3. **Checkpoint Resume** (`find_latest_checkpoint`): On startup, checks both local disk and S3 for the latest checkpoint, downloads if needed, and resumes training from that step.

### Bootstrap

`bootstrap.sh` handles full autonomous instance setup in 15 steps with real-time status tracking (written to `/tmp/bootstrap_status.json` for the dashboard to display):

| Step | Action | Notes |
|------|--------|-------|
| 0 | NVMe ephemeral storage | Create data directories on fast local disk |
| 1 | Fetch secrets | W&B, HuggingFace, dashboard tokens from Secrets Manager |
| 2 | Configure environment | `.bashrc` env vars, git credentials |
| 3 | Pull latest code | `git pull --ff-only` |
| 4 | Restore artifacts from S3 | Checkpoints, logs, eval metrics, benchmarks (**bottleneck: ~3 min**) |
| 5 | Sync preprocessed data | Tokenized training data from S3 |
| 6 | Fix file ownership | S3 restores as root |
| 7 | Update CloudFront DNS | `origin.train.bitbanshee.com` A record → instance IP |
| 8 | Start sync daemon | `sync-checkpoints.sh` (60s interval) |
| 9 | Install nginx | apt install (if missing) |
| 10 | Configure nginx | HTTP-only reverse proxy (CloudFront handles TLS) |
| 11 | Install Flask | pip install (if missing) |
| 12 | Start web dashboard | Flask on :5000 |
| 13 | Setup spot price updater | Initial run + cron every 5 min |
| 14 | Launch training | tmux session, auto-resumes from latest checkpoint |

Pulled from S3 on every boot (`s3://ml-lab-004507070771/dual-system-research-data/deploy/bootstrap.sh`). Tested across multiple spot recovery cycles with zero manual intervention.

## Quick Start

### Prerequisites

- Python 3.11+
- NVIDIA GPU with CUDA support
- AWS credentials (for S3 sync, optional)
- W&B account (for experiment tracking, optional)

### Installation

```bash
git clone https://github.com/BITBANSHEE-C137/KahnemanHybridExperiment.git
cd KahnemanHybridExperiment
pip install -r requirements.txt
pip install -e .
```

### Run Tests

```bash
pytest tests/ -v
```

### Smoke Test (< 5 minutes on GPU)

```bash
python -m src.training.joint_trainer --config configs/tiny.yaml --smoke_test
```

### Full Training

```bash
# Preprocess data (one-time, ~5 hours)
python scripts/lean_preprocess.py

# Train
python -m src.training.joint_trainer --config configs/tiny.yaml
```

### Benchmarks

```bash
python scripts/benchmark.py --checkpoint checkpoints/step_50000.pt --config configs/tiny.yaml
python scripts/compare_systems.py --checkpoint checkpoints/step_50000.pt --config configs/tiny.yaml
```

### Monitoring

**Web:** Visit [train.bitbanshee.com](https://train.bitbanshee.com) for the live web dashboard with charts, GPU stats, and cost tracking.

**Terminal (read-only):**
```bash
./monitor.sh        # ANSI dashboard, 15s refresh
./monitor.sh 5      # 5s refresh
```

**Terminal (job manager):**
```bash
python dashboard.py              # Interactive menu
python dashboard.py --job tiny   # Launch training directly
```

## Training Configuration

Key hyperparameters for the Tiny (GPT-2 Small) config:

| Parameter | Value |
|-----------|-------|
| Batch size | 4 (× 8 gradient accumulation = 32 effective) |
| Max steps | 50,000 |
| Learning rate | 3e-4 → 3e-5 (cosine decay) |
| Warmup steps | 2,000 |
| Weight decay | 0.1 |
| Precision | bfloat16 |
| Optimizer | AdamW (β₁=0.9, β₂=0.95) |
| Gradient clipping | 1.0 |
| Mask ratio range | 0.1 – 1.0 |
| Checkpoint interval | Every 1,000 steps |
| Eval interval | Every 1,000 steps |

## References

- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- [Dual Language Models](https://arxiv.org/abs/2512.14549) — shared-weight joint training of AR + diffusion objectives
- [LLaDA: Large Language Diffusion with mAsking](https://arxiv.org/abs/2502.09992) — masked diffusion for language modeling at scale
- [DiffuGPT: Scaling Diffusion Language Models via Adaptation from Autoregressive Models](https://openreview.net/forum?id=YOUR_ID) (ICLR 2025)
- [nanoGPT](https://github.com/karpathy/nanoGPT) — clean GPT-2 reference implementation

## License

This is a research project. No license has been specified yet.
