# KahnemanHybridExperiment

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
├── bootstrap.sh                     # EC2 instance setup + S3 restore
├── sync-checkpoints.sh              # S3 artifact sync daemon
├── dashboard.py                     # Curses-based training monitor TUI
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

*Experiments in progress. Results will be added upon completion.*

## Infrastructure

### AWS Setup

- **Compute**: EC2 Spot Fleet (g5.2xlarge / g6.xlarge) with NVIDIA A10G or L4 GPUs
- **Storage**: Instance NVMe for fast I/O, S3 for persistence (`s3://ml-lab-004507070771/dual-system-research-data/`)
- **Secrets**: AWS Secrets Manager for W&B and HuggingFace tokens
- **Tracking**: [Weights & Biases](https://wandb.ai) for real-time experiment logging

### Spot Instance Resilience

Training runs on spot instances with three layers of protection:

1. **S3 Sync Daemon** (`sync-checkpoints.sh`): Uploads checkpoints, logs, metrics, and preprocessed data to S3 every 60 seconds.
2. **SIGTERM Handler** (`SpotTerminationHandler`): Catches the 2-minute termination warning and performs a final S3 sync before the instance dies.
3. **Checkpoint Resume** (`find_latest_checkpoint`): On startup, checks both local disk and S3 for the latest checkpoint, downloads if needed, and resumes training from that step.

### Bootstrap

`bootstrap.sh` handles full instance setup: mounts NVMe, fetches secrets, restores artifacts from S3, starts the sync daemon, and launches training in a tmux session. New spot instances are fully autonomous.

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

### Dashboard

```bash
python dashboard.py
```

A terminal UI for launching and monitoring training runs with live metrics, GPU stats, and scrollable logs.

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
| Checkpoint interval | Every 5,000 steps |
| Eval interval | Every 1,000 steps |

## References

- Kahneman, D. (2011). *Thinking, Fast and Slow*. Farrar, Straus and Giroux.
- [Dual Language Models](https://arxiv.org/abs/2512.14549) — shared-weight joint training of AR + diffusion objectives
- [LLaDA: Large Language Diffusion with mAsking](https://arxiv.org/abs/2502.09992) — masked diffusion for language modeling at scale
- [DiffuGPT: Scaling Diffusion Language Models via Adaptation from Autoregressive Models](https://openreview.net/forum?id=YOUR_ID) (ICLR 2025)
- [nanoGPT](https://github.com/karpathy/nanoGPT) — clean GPT-2 reference implementation

## License

This is a research project. No license has been specified yet.
