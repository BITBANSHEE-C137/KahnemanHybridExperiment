# CLAUDE.md — KahnemanHybridExperiment

This file is the operational prompt for Claude Code sessions on this repo.
Glenn is the architect and decision-maker. Claude Code is the implementer.
For research review, architectural questions, or sanity checks, Glenn consults Claude Opus via claude.ai.

## What This Project Is

A dual-process language model experiment. One Transformer (GPT-2), two cognitive modes:

- **System 1 (diffusion/iterative unmasking)**: Bidirectional attention. Predict masked tokens in parallel. Fast, cheap, default mode.
- **System 2 (autoregressive)**: Causal attention. Standard left-to-right generation. Slow, expensive, escalation mode.

Same weights, different attention masks. A trained confidence head decides when System 1's output is trustworthy vs. when to escalate to System 2.

**Joint training objective:** `L = λ_ar · L_ar + λ_diff · L_diff + λ_conf · L_conf`

**Inspired by:** Kahneman's *Thinking, Fast and Slow*. **Related work:** LLaDA (masked diffusion), Dual Language Models (Samuel & Charpentier 2025), speculative decoding (inverted — same model, two modes, learned gate).

## Project State

### Training Status

**v1 Baseline: COMPLETE** (March 1–3, 2026)
- GPT-2 Small (124M), 50k steps, OpenWebText
- 3/5 targets met. See README.md for full results.

**v2 Training: IN PROGRESS** (March 4+, 2026)
- Same config (`configs/tiny.yaml`), λ_diff increased 1.0→2.0
- Eval metrics stored in `eval_metrics/v2/` (S3), v1 archived in `eval_metrics_v1/`
- Automated cost controls active: $50 budget cap, $0.75/hr spot ceiling

### v2 Metrics (Latest)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AR Perplexity | 31.05 | < 40 | ✅ Met |
| S1 Token Accuracy | 26.1% | > 40% | 🔶 Stalled |
| Diffusion Loss | 4.33 | < 4.0 | 🔶 Improving |
| Confidence AUROC | 0.852 | > 0.75 | ✅ Met |
| Confidence ECE | 0.014 | < 0.05 | ✅ Met |

## Repository Layout

```
KahnemanHybridExperiment/
├── configs/tiny.yaml                 # Training config (hyperparams, loss weights, masking)
├── src/
│   ├── model/
│   │   ├── dual_process_gpt2.py      # DualProcessGPT2 model + ConfidenceHead
│   │   └── masking.py                # LLaDA-style random masking
│   ├── training/
│   │   └── joint_trainer.py          # Main training loop (AR + diffusion + confidence)
│   ├── evaluation/
│   │   ├── evaluator.py              # Eval loop (PPL, accuracy, ECE, AUROC)
│   │   └── metrics.py                # AUROC implementation
│   ├── inference/
│   │   └── generator.py              # System 1, System 2, Hybrid generation
│   ├── data/
│   │   └── openwebtext.py            # Memmap + HuggingFace data loading
│   └── utils/
│       └── s3_sync.py                # S3 uploads, spot termination handler
├── scripts/
│   ├── benchmark.py                  # LAMBADA + WikiText-103 eval
│   ├── compare_systems.py            # S1 vs S2 analysis
│   ├── lean_preprocess.py            # Memory-efficient tokenization
│   └── prepare_openwebtext.py        # Streaming data preprocessing
├── tests/                            # pytest suite (model, training, eval, data, inference)
├── web_dashboard.py                  # Live Flask dashboard (SSE + Chart.js)
├── monitor.sh                        # Terminal ANSI dashboard
├── dashboard.py                      # Curses TUI job launcher
├── bootstrap.sh                      # Autonomous spot instance recovery
├── sync-checkpoints.sh               # S3 artifact sync daemon
├── update-dns.sh                     # Route53 DNS auto-update
├── update-spot-price.sh              # Spot price cron job
├── cost-tracker.sh                   # Session cost ledger
├── CLAUDE.md                         # THIS FILE — Claude Code prompt
├── STATUS.md                         # Training progress + metrics history
├── INFRASTRUCTURE.md                 # AWS setup, bootstrap, networking
└── README.md                         # Full research narrative + results
```

## Architecture Details (for making changes)

### Model (`src/model/dual_process_gpt2.py`)

- `DualProcessGPT2` wraps `GPT2LMHeadModel` from HuggingFace
- `_forward_transformer()` manually iterates over transformer blocks with a custom 4D attention mask. This is how System 1 gets bidirectional attention. **This is fragile across transformers versions — pinned to 5.2.0.**
- `forward_system1()` → bidirectional mask → logits + confidence + hidden
- `forward_system2()` → HF built-in causal mask → logits only
- `ConfidenceHead` is a 2-layer MLP (`Linear → GELU → Linear`) producing per-token logits
- `compute_confidence_loss()` uses BCE on masked positions only. Target: did S1 predict the correct token?
- Mask token: `<|endoftext|>` (token 50256) repurposed. No vocab expansion.

### Training (`src/training/joint_trainer.py`)

- Each step: AR loss + diffusion loss + confidence loss, weighted sum, gradient accumulation
- Cosine LR with linear warmup (2k steps warmup, 50k total)
- Mixed precision (bfloat16), gradient clipping (1.0), AdamW (β₁=0.9, β₂=0.95)
- Checkpoint resume from local disk or S3
- SIGTERM handler for spot termination → final S3 sync
- Local checkpoint retention: keep last 3, S3 has all

### Inference (`src/inference/generator.py`)

- `generate_system1()`: Start fully masked → iteratively unmask most-confident positions
- `generate_system2()`: Standard autoregressive with top-k
- `generate_hybrid()`: S1 first → score confidence → escalate to S2 if low

### Data (`src/data/openwebtext.py`)

- Preferred: pre-tokenized uint16 memmap `.bin` files (zero-copy, fast)
- Fallback: HuggingFace streaming tokenization (slow, for smoke tests)
- Eval split: separate `openwebtext_eval.bin` or last N docs from HF

### Infrastructure

- **S3:** `s3://ml-lab-004507070771/dual-system-research-data/`
- **Instance:** g5.2xlarge / g6.xlarge spot fleet (A10G / L4 GPU)
- **Fleet:** `fleet-2840fcd1-6c2d-44c0-ad17-7f3799ca6c9a`
- **AMI:** `ami-0f6e32b2ebf1c8a2d` (clean — no secrets baked in)
- **Launch template:** `lt-06e111b12bd85396f` v19
- **Volumes:** ~100GB EBS root + NVMe ephemeral at `/opt/dlami/nvme`
- **EBS static data:** Tagged `ml-lab-static-data` volumes for preprocessed data (one per AZ)
- **Data:** Preprocessed OpenWebText at `/opt/dlami/nvme/ml-lab/preprocessed/`
- **Checkpoints:** `/opt/dlami/nvme/ml-lab/checkpoints/v2/` + S3
- **Dashboard:** CloudFront → nginx → Flask :5000 at https://train.bitbanshee.com
- **DNS:** `train.bitbanshee.com` (CloudFront ALIAS), `origin.train.bitbanshee.com` (EC2 A record)
- **Secrets:** AWS Secrets Manager (7 secrets in `ml-lab/*` prefix — all fetched at boot, nothing baked)
- **Notifications:** Telegram bot for spot reclaims, budget alerts, price ceiling, sitreps
- **IAM:** `ml-lab-ec2-bootstrap` role (S3, Secrets Manager, EC2, Route53, EBS)
- **Bootstrap:** `s3://.../deploy/bootstrap.sh` → pulled on every boot (18 autonomous steps)
- **Cost controls:** $50 budget cap + $0.75/hr spot ceiling, both with Telegram alerts

### Secrets & Credentials

The AMI contains no secrets. All credentials are fetched from AWS Secrets Manager at bootstrap Step 1:
- `ml-lab/wandb-api-key` — W&B experiment tracking
- `ml-lab/hf-token` — HuggingFace model downloads
- `ml-lab/dashboard-spot-token` — Dashboard write API auth
- `ml-lab/claude-api-key` — Claude API for sitrep generation
- `ml-lab/telegram-bot-token` — Telegram notifications
- `ml-lab/telegram-chat-id` — Telegram chat destination
- `ml-lab/gh-token` — GitHub push access

Secrets are written to `~/.bashrc` as exports. Cron jobs receive them inline (cron doesn't source `.bashrc`).

### Telegram Notifications

Telegram bot sends alerts for: bootstrap complete, spot reclaim, budget exceeded, spot price ceiling hit, sitrep delivery. All notifications use `send_telegram()` from `auto_sitrep.py`. Env vars (`TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID`) are passed inline to cron jobs and the dashboard process since cron doesn't source `.bashrc`.

### Cost Controls

Two automated circuit breakers:
- **Budget cap** ($50): `cost-tracker.sh` checks every 5 min. Sends Telegram alert + sets fleet capacity to 0.
- **Spot price ceiling** ($0.75/hr): `update-spot-price.sh` checks every 5 min. Sends Telegram alert + sets fleet capacity to 0.

Both thresholds configurable via env vars (`MAX_BUDGET`, `MAX_SPOT_PRICE`).

## Known Issues & v2 Fix Queue

These are ordered by priority. Implement in this order.

### 1. CRITICAL — Confidence Scoring Distribution Mismatch

**File:** `src/inference/generator.py`, `generate_hybrid()`

**Bug:** Confidence head is trained on masked positions but evaluated in hybrid mode on a fully-unmasked sequence (all-False mask). Distribution mismatch makes hybrid escalation decisions invalid.

**Fix:** Accumulate confidence scores during the iterative unmasking loop in `generate_system1()`, at the moment each position is revealed. Return that aggregate. Use it in `generate_hybrid()` instead of post-hoc re-scoring.

**Implementation:**

In `generate_system1()`:
- Add `accumulated_conf` and `conf_count` tensors (zeros, shape `(1, seq_len)`)
- Inside the unmasking loop, when unmasking position `(row, col)`, record `conf_scores[row, col]` into `accumulated_conf`
- Change return signature to `(ids, mean_confidence)` where `mean_confidence = accumulated_conf.sum() / conf_count.sum().clamp(min=1)`

In `generate_hybrid()`:
- Call the updated `generate_system1()` and use the returned confidence directly
- Remove the post-hoc `forward_system1(ids, mask_dummy)` block entirely

**Validation:**
- Hybrid escalation should now correlate with actual S1 reconstruction quality
- Log escalation rate at various thresholds [0.5, 0.6, 0.7, 0.8, 0.9] during eval
- Compare escalation rates between v1 (broken signal) and v2 (correct signal)

### 2. LOW — Dead Code in `forward_system2`

**File:** `src/model/dual_process_gpt2.py`, `forward_system2()`

**Bug:** Lines ~114-119 recompute embeddings (`wte + wpe + drop`) after a full forward pass, assign to `hidden`, then return `None` for `hidden_states`. Dead code.

**Fix:** Delete the embedding recomputation. The method should be:

```python
def forward_system2(self, input_ids):
    outputs = self.transformer(input_ids, output_hidden_states=False)
    return outputs.logits, None
```

### 3. MEDIUM — Prompt-Conditioned System 1 Generation

**File:** `src/inference/generator.py`, `generate_system1()`

**Feature:** Add optional `prompt_ids` parameter. If provided, keep the first `prompt_ids.size(1)` positions unmasked with the prompt tokens. Only mask/unmask the suffix.

**Implementation:**
- New parameter: `prompt_ids: Optional[torch.Tensor] = None`
- After initializing `ids` and `mask`, if `prompt_ids is not None`: set `ids[0, :P] = prompt_ids[0]` and `mask[0, :P] = False`
- Rest of unmasking loop unchanged (only operates on `mask=True` positions)
- Update `generate_hybrid()` to pass prompt if available

### 4. MEDIUM — System 2 / Manual Loop Parity Test

**File:** `tests/test_model.py` (new test)

**Purpose:** Validate that `_forward_transformer()` with a causal mask produces identical logits to HF's built-in `forward_system2()` path. Guards against silent breakage when transformers version changes.

**Implementation:**

```python
def test_system2_matches_manual_causal():
    """System 2 logits must match manual forward with causal mask."""
    config = load_tiny_config()
    model = DualProcessGPT2(config, pretrained=True).eval()
    input_ids = torch.randint(0, 50257, (1, 64))

    logits_hf, _ = model.forward_system2(input_ids)

    T = input_ids.size(1)
    causal_mask = torch.tril(torch.ones(1, 1, T, T))
    logits_manual, _ = model._forward_transformer(input_ids, causal_mask)

    assert torch.allclose(logits_hf, logits_manual, atol=1e-4), \
        f"Max diff: {(logits_hf - logits_manual).abs().max().item()}"
```

### 5. LOW — Document Eval Split Provenance

**Files:** `src/data/openwebtext.py`, `scripts/lean_preprocess.py`

**Task:** Add comments documenting how `openwebtext_eval.bin` was created and confirming non-overlap with `openwebtext_train.bin`. If overlap exists at chunk boundaries, document it.

### 6. LOW — Terminology Cleanup

**Files:** `README.md`, `STATUS.md`, docstrings

**Task:** Where "diffusion" appears without LLaDA framing, clarify as "iterative masked denoising/unmasking." The generation process is not a continuous diffusion process — it's discrete iterative unmasking with confidence-ordered revealing. The term "diffusion" is acceptable when referencing the loss/objective (following LLaDA convention) but the generation procedure should be described precisely.

## v2 New Metrics to Add

After implementing fixes 1-4, add these to the eval loop and dashboard:

- Hybrid escalation rate at thresholds [0.5, 0.6, 0.7, 0.8, 0.9]
- Generation confidence distribution (histogram of mean confidence per sequence)
- Tokens saved by S1 (when hybrid doesn't escalate)
- Latency/throughput comparison (pure AR vs S1 vs hybrid)

## v2 Comparison Plan

v2 runs identical `configs/tiny.yaml`, same data, same 50k steps. Only changes are the fixes above. Compare:

- AUROC trajectory (should be similar — training-time signal was correct)
- Hybrid escalation rate (new metric, not available in v1)
- AR PPL trajectory (should be identical — fixes don't touch training)
- S1 token accuracy trajectory (should be identical)

Key question: does fixing the confidence signal change anything about training, or was only inference affected?

## Environment

| Package | Version | Notes |
|---------|---------|-------|
| Python | 3.12.10 | |
| PyTorch | 2.6.0+cu124 | |
| CUDA | 12.4 | driver 580.126.09 |
| transformers | 5.2.0 | Pinned — manual block loop depends on internal API |
| datasets | 4.6.0 | |
| accelerate | 1.12.0 | |
| wandb | 0.25.0 | |

## Conventions

- All S3 operations are non-blocking (threaded) and wrapped in try/except. S3 failures never crash training.
- Checkpoints include both model and optimizer state for exact resume.
- Config is the single source of truth for hyperparameters. Don't hardcode values that belong in `tiny.yaml`.
- Tests use `--smoke_test` config overrides for fast validation.
- Commit messages should reference the fix number from the queue above (e.g., "fix #1: accumulate confidence during unmasking").
- When in doubt about an architectural decision, stop and ask. Glenn consults Claude Opus for sanity checks.

## Multi-Model Audit (2026-03-01)

This repo was reviewed by ChatGPT 5.2, Grok, Gemini, and Claude Opus 4.6. All four agreed:

- Research question is well-posed and testable
- Engineering is unusually strong for a solo research project
- Confidence scoring mismatch is the one critical fix
- v1 should complete as-is for a clean baseline
- Project is worth continuing

Full audit details in the review document. Findings are incorporated into the fix queue above.
