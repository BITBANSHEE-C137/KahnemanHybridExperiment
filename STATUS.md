# Project Status — Dual-Process Language Model

**Last updated:** 2026-02-28

## Live Dashboard

**[train.bitbanshee.com](https://train.bitbanshee.com)** — real-time training metrics, GPU stats, loss curves, and cost tracking.

## Training Progress

| Metric | Value |
|---|---|
| Current step | 4,100 / 50,000 (8.2%) |
| Phase | Cosine decay (warmup complete at step 2,000) |
| Elapsed | ~7 hours |
| Instance | g5.2xlarge (NVIDIA A10G, spot) |

### Latest Train Metrics (step 4,100)

| Metric | Value |
|---|---|
| AR Loss | 3.197 |
| Diffusion Loss | 6.168 |
| Confidence Accuracy | 91.5% |
| Learning Rate | 2.99e-4 |

### Eval History

| Step | AR PPL | Diff Loss | S1 Token Acc | Conf ECE | Conf AUROC |
|------|--------|-----------|-------------|----------|------------|
| 50 | 19,060 | 7.84 | 3.4% | 0.0499 | 0.466 |
| 100 | 23,331 | 7.57 | 3.2% | 0.0037 | 0.502 |
| 1,000 | 22,005 | 6.88 | 5.2% | 0.0002 | 0.548 |
| 2,000 | 25,008 | 6.66 | 6.0% | 0.0030 | 0.594 |
| 3,000 | 21,412 | 6.52 | 7.1% | 0.0057 | 0.628 |
| 4,000 | 22,406 | 6.23 | 8.6% | 0.0052 | 0.669 |

**Trends:** Diffusion loss steadily declining (7.84 → 6.23). S1 token accuracy 2.5× baseline (3.4% → 8.6%). Confidence AUROC improving (0.47 → 0.67), indicating the confidence head is learning to distinguish correct from incorrect predictions. AR perplexity still high — expected early in training with joint objectives competing for shared weights.

## Infrastructure

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance type | Active | g5.2xlarge / g6.xlarge (spot fleet) |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data |
| Deploy scripts | Updated | bootstrap.sh, sync-checkpoints.sh in S3 |
| Web dashboard | Live | [train.bitbanshee.com](https://train.bitbanshee.com) — nginx + TLS + Flask |
| DNS | Automated | Route53 A record updated on boot via systemd unit |

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

## Completed

- [x] S3 bucket consolidation
- [x] Deploy scripts updated with correct bucket paths
- [x] Python 3.12 set as default `python3`
- [x] Full ML stack installed to EBS
- [x] GPU verified — A10G detected, CUDA matmul confirmed
- [x] requirements.txt created
- [x] Project source code built (src/, configs/, tests/)
- [x] AMI snapshot with current environment
- [x] First smoke test on tiny config
- [x] OpenWebText preprocessing (memmap shards)
- [x] Full training launched on tiny config (GPT-2 Small, 50k steps)
- [x] Web dashboard — live at [train.bitbanshee.com](https://train.bitbanshee.com)
- [x] HTTPS + nginx reverse proxy with Let’s Encrypt TLS
- [x] Dashboard hardened — token auth on write endpoints, SSE limits, security headers
- [x] Route53 DNS auto-update on instance boot

## Next Steps

- [ ] Complete training run (50,000 steps)
- [ ] Run LAMBADA + WikiText-103 benchmarks at final checkpoint
- [ ] Run system comparison analysis (System 1 vs 2)
- [ ] Scale to GPT-2 Medium (355M) tier
