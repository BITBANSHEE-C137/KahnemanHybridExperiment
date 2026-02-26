# Project Status

## Current Tier: Tiny (GPT-2 Small, 124M params)

## What's Built

### Core Architecture — `src/model/`
- [x] `dual_process_gpt2.py` — Shared-weight GPT-2 with System 1 (bidirectional diffusion) and System 2 (causal AR) modes
- [x] `masking.py` — LLaDA-style random token masking with configurable ratio range
- [x] `ConfidenceHead` — MLP predicting per-token confidence from hidden states

### Training — `src/training/`
- [x] `joint_trainer.py` — Joint training loop: AR loss + diffusion loss + confidence loss
- [x] Cosine LR schedule with linear warmup
- [x] Gradient accumulation, mixed precision (bfloat16), gradient clipping
- [x] W&B logging (optional, graceful fallback)
- [x] Local checkpointing every N steps
- [x] Evaluation loop integrated (runs every `eval_every` steps)

### Evaluation — `src/evaluation/`
- [x] `evaluator.py` — `evaluate()` computes 6 metrics over held-out eval batches
- [x] `metrics.py` — Standalone AUROC (no sklearn dependency)
- [x] Metrics: AR perplexity, diffusion loss, System 1 token accuracy, confidence accuracy, ECE, AUROC
- [x] Training loop integration: replaces `conf_acc=0.0` placeholder with real eval values

### Inference — `src/inference/`
- [x] `generator.py` — Three generation modes:
  - System 1: iterative diffusion unmasking (fully masked -> progressive reveal)
  - System 2: standard AR generation with top-k sampling
  - Hybrid: System 1 first, escalate to System 2 if mean confidence < threshold

### Data — `src/data/`
- [x] `openwebtext.py` — OpenWebText loader with tokenization + chunking
- [x] `create_dataloader()` for training
- [x] `create_eval_dataloader()` using tail slice of OpenWebText as held-out eval

### Config — `configs/`
- [x] `tiny.yaml` — GPT-2 Small (124M), single A10G, all hyperparameters + smoke_test overrides

### Tests
- [x] 43 tests passing (`pytest tests/ -v`)
- [x] `test_model.py` — Model shapes, losses, masking, shared weights (18 tests)
- [x] `test_inference.py` — All three generation modes (5 tests)
- [x] `test_training.py` — LR schedule (5 tests)
- [x] `test_evaluation.py` — AUROC, ECE, full evaluate pipeline (20 tests -- note: 5 overlap from metrics)

## Infrastructure

| Component | Status | Details |
|---|---|---|
| S3 bucket | Migrated | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance type | Active | g5.2xlarge — NVIDIA A10G (24GB VRAM) |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack (37GB used) |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data (HF cache, checkpoints) |
| Deploy scripts | Updated | bootstrap.sh, sync-checkpoints.sh, dashboard.py in S3 |

## Environment (baked into AMI)

| Package | Version |
|---|---|
| Python | 3.12.10 |
| PyTorch | 2.6.0+cu124 |
| CUDA | 12.4 (driver 580.126.09) |
| transformers | 5.2.0 |
| datasets | 4.6.0 |
| accelerate | 1.12.0 |
| wandb | 0.25.0 |
| safetensors | 0.7.0 |
| einops | 0.8.2 |
| scipy | 1.17.1 |

## What's Not Built Yet

### Config
- [ ] `configs/small.yaml` — GPT-2 Medium (355M params, 24 layers, 1024 embed)
- [ ] `configs/medium.yaml` — GPT-2 Large (774M params, 36 layers, 1280 embed)

### Scripts — `scripts/`
- [ ] Shell scripts for launching training jobs
- [ ] SageMaker job launcher for Tier 3 (8xA100)

### Infrastructure
- [ ] S3 checkpoint upload (currently saves to local disk only)
- [ ] Checkpoint resume (load from existing checkpoint and continue training)

### Evaluation Enhancements
- [ ] Generation quality metrics (BLEU, MAUVE, etc.)
- [ ] Benchmark suite (e.g., HellaSwag, LAMBADA)
- [ ] System 1 vs System 2 comparison on downstream tasks

### Other
- [ ] `notebooks/` — Analysis and visualization notebooks
- [ ] `paper/` — Draft and figures

## Entry Points

```bash
# Full training
python -m src.training.joint_trainer --config configs/tiny.yaml

# Smoke test (<5 min on GPU)
python -m src.training.joint_trainer --config configs/tiny.yaml --max_steps 100 --smoke_test

# Run tests
pytest tests/ -v
```

## Changelog

### 2026-02-26
- **Evaluation module** — Added `src/evaluation/` with `evaluate()`, AUROC, ECE, confidence accuracy. Integrated into training loop every `eval_every` steps. Added `create_eval_dataloader()`. 20 new tests.
- **Initial implementation** — Full tiny-tier scaffold: model (`DualProcessGPT2`, `ConfidenceHead`, masking), joint trainer (3 losses, cosine LR, grad accum, mixed precision, W&B), inference (System 1/2/hybrid generation), OpenWebText data loader, `configs/tiny.yaml`, 23 tests.
- **Project setup** — `CLAUDE.md`, `.gitignore`, `requirements.txt`, `setup.py`, directory structure.
