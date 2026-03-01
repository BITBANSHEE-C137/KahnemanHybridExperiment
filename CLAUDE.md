# CLAUDE.md — Dual-Process Language Model

> This file tells Claude Code what this project is, how to work in it,
> and what conventions to follow. Claude Code reads this automatically.

## Project Overview

This is a research project building a **dual-process language model** — a single
Transformer that operates in two cognitive modes:

- **System 1 (Diffusion)**: Fast, parallel token generation via masked diffusion. Default mode.
- **System 2 (Autoregressive)**: Slow, sequential token generation via standard causal LM. Escalation mode.

A trained **confidence head** decides whether System 1's output is good enough to
ship, or whether to escalate to System 2. This is a System 1-led architecture —
diffusion generates first, autoregressive reasoning only engages when confidence
is low.

The architecture uses shared weights. The only difference between modes is the
attention mask (bidirectional vs causal). Joint training with both objectives
produces weights that work in either mode.

## Model Family

All experiments use the GPT-2 family with the same tokenizer (50257 vocab):
- Tier 1 (Tiny): GPT-2 Small — 124M params, 12 layers, 768 embed dim
- Tier 2 (Small): GPT-2 Medium — 355M params, 24 layers, 1024 embed dim
- Tier 3 (Medium): GPT-2 Large — 774M params, 36 layers, 1280 embed dim

Initialize from HuggingFace pretrained weights. Do not train from scratch.

## Tech Stack

- Python 3.11+, PyTorch 2.5+
- HuggingFace transformers (for weight loading and tokenizer only)
- Weights & Biases for experiment tracking
- YAML configs in `configs/`
- Training data: OpenWebText via HuggingFace datasets

## Code Conventions

- Type hints on all function signatures
- Docstrings on all public functions (Google style)
- No notebooks for core logic — notebooks are for analysis only
- Config-driven: all hyperparameters in YAML, never hardcoded
- Checkpoint every N steps to S3 automatically
- Log to W&B every 100 steps
- Print training metrics in format: `step: N | ar_loss: X.XX | diff_loss: X.XX | conf_acc: X.XX`
  (SageMaker parses these regexes for metrics)

## Directory Structure

```
KahnemanHybridExperiment/
├── CLAUDE.md               # This file — project conventions for Claude Code
├── README.md               # Research narrative (motivation, related work, results)
├── INFRASTRUCTURE.md       # Ops & deployment (spot recovery, dashboards, cost)
├── STATUS.md               # Live training status and environment details
├── requirements.txt
├── setup.py
├── configs/
│   └── tiny.yaml           # GPT-2 Small training config
├── src/
│   ├── model/              # Architecture (dual_process_gpt2.py, masking.py)
│   ├── training/           # Training loop (joint_trainer.py)
│   ├── inference/          # Generation pipelines (generator.py)
│   ├── data/               # Data loading (openwebtext.py)
│   └── evaluation/         # Eval & metrics (evaluator.py, metrics.py)
├── scripts/                # Benchmarks & data preprocessing
├── tests/                  # pytest test suite
├── bootstrap.sh            # Autonomous EC2 spot recovery
├── web_dashboard.py        # Live web dashboard (Flask + SSE)
├── monitor.sh              # Terminal training monitor (ANSI)
└── dashboard.py            # Curses TUI job launcher
```

## GPU Environment

- Tier 1-2: Single NVIDIA A10G (24GB VRAM) on AWS g5 instances
- Tier 3: 8x NVIDIA A100 40GB (320GB total) on AWS p4d via SageMaker
- Always use mixed precision (bfloat16) for training
- Always use gradient checkpointing for models > 200M params

## Key References

- "Dual Language Models" (arxiv 2512.14549) — proved shared-weight joint training works
- "Large Language Diffusion Models" / LLaDA (arxiv 2502.09992) — masked diffusion at scale
- "Scaling Diffusion Language Models via Adaptation from Autoregressive Models" (ICLR 2025) — DiffuGPT
- nanoGPT by Karpathy — clean GPT-2 reference implementation
- "Chain of Thought Monitorability" (arxiv 2507.11473) — safety context

## Documentation

| Document | Contents |
|----------|----------|
| [README.md](README.md) | Research narrative — abstract, motivation, related work, architecture, results, reproducibility |
| [INFRASTRUCTURE.md](INFRASTRUCTURE.md) | Operational details — AWS architecture, spot recovery, bootstrap, dashboards, cost analysis |
| [STATUS.md](STATUS.md) | Live training status, environment versions, completed milestones, next steps |
| [CLAUDE.md](CLAUDE.md) | This file — project conventions, code standards, GPU environment |

## Current Training Status (2026-03-01)

Training GPT-2 Small (124M) on OpenWebText, step ~10,700 / 50,000 (21%).
Three of seven targets met: AR PPL (<40), AUROC (>0.75), ECE (<0.05).

Key findings:
- Confidence AUROC crossed 0.75 at step 8,000 — hybrid escalation mechanism validated
- AR PPL ~26.5 (better than pretrained baseline ~31.5, drifting up slowly due to objective interference)
- Diffusion loss 5.41 (64% of reduction toward 4.0 target)
- S1 token accuracy 14.7% (accelerating, targeting 40%)

## Known Bugs (Fixed)

- **AR PPL double-shift** (fixed 2026-03-01): evaluator.py, benchmark.py, and
  compare_systems.py manually shifted labels before `compute_ar_loss()`, which
  auto-shifts internally via HuggingFace. This inflated eval AR PPL by ~1000x.
  All historical checkpoints re-evaluated via `scripts/reeval_checkpoints.py`.
- **Bash `local` scope** (fixed 2026-03-01): `local a=$((expr)) b=$((a))` in
  monitor.sh gauge/pbar functions — bash evaluates b before a is assigned in the
  same `local` declaration. Split into separate `local` statements.

## License

MIT License. See [LICENSE](LICENSE).

## Testing

Run tests before committing:
```bash
pytest tests/ -v
```

Run a quick smoke test on tiny config (should complete in <5 min on GPU):
```bash
python -m src.training.joint_trainer --config configs/tiny.yaml --max_steps 100 --smoke_test
```
