# Project Status — Dual-Process Language Model

**Last updated:** 2026-02-28

## Live Dashboard

**[train.bitbanshee.com](https://train.bitbanshee.com)** — real-time training metrics, GPU stats, loss curves, and cost tracking.

## Training Progress

| Metric | Value |
|---|---|
| Current step | ~200 / 50,000 (resuming from step 100 checkpoint) |
| Phase | Warmup (cosine decay begins at step 2,000) |
| Instance | g5.2xlarge (NVIDIA A10G, spot) |

**Note:** Steps 100–4,000+ from the initial run were lost across spot terminations before checkpoint frequency was increased. Checkpoint interval is now every 1,000 steps (was 5,000). The eval history below is from the prior run and represents validated training dynamics.

### Eval History (prior run)

| Step | AR PPL | Diff Loss | S1 Token Acc | Conf ECE | Conf AUROC |
|------|--------|-----------|-------------|----------|------------|
| 1,000 | 22,005 | 6.88 | 5.2% | 0.0002 | 0.548 |
| 2,000 | 25,008 | 6.66 | 6.0% | 0.0030 | 0.594 |
| 3,000 | 21,412 | 6.52 | 7.1% | 0.0057 | 0.628 |

**Trends:** Diffusion loss steadily declining (7.84 → 6.52). S1 token accuracy doubled from random baseline. Confidence AUROC improving (0.47 → 0.63), indicating the confidence head is learning to distinguish correct from incorrect predictions. These trends are expected to reproduce and continue in the current run.

## Infrastructure

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance type | Active | g5.2xlarge / g6.xlarge (spot fleet) |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data |
| Bootstrap | Autonomous | Fully autonomous spot recovery with TLS cert backup/restore |
| Web dashboard | Live | [train.bitbanshee.com](https://train.bitbanshee.com) — nginx + Flask |
| DNS | Automated | Route53 A record updated on boot via bootstrap |
| Spot price | Automated | Cron job updates dashboard every 5 minutes |
| Sync daemon | Active | S3 artifact sync every 60 seconds |

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
- [x] GPU verified — L4/A10G detected, CUDA matmul confirmed
- [x] requirements.txt created
- [x] Project source code built (src/, configs/, tests/)
- [x] AMI snapshot with current environment
- [x] First smoke test on tiny config
- [x] OpenWebText preprocessing (memmap shards)
- [x] Full training launched on tiny config (GPT-2 Small, 50k steps)
- [x] Web dashboard — live at [train.bitbanshee.com](https://train.bitbanshee.com)
- [x] HTTPS + nginx reverse proxy with Let's Encrypt TLS
- [x] Dashboard hardened — token auth on write endpoints, SSE limits, security headers
- [x] Route53 DNS auto-update on instance boot
- [x] Fully autonomous bootstrap — all services start without manual intervention
- [x] Checkpoint frequency increased to every 1,000 steps
- [x] Local checkpoint cleanup (keep last 3, S3 has all)
- [x] Spot price monitoring via cron + IMDSv2 auto-detection
- [x] TLS cert backup/restore via S3 (handles Let's Encrypt rate limits)
- [x] Bootstrap battle-tested across 4 spot recovery cycles

## Next Steps

- [ ] Complete training run (50,000 steps)
- [ ] Run LAMBADA + WikiText-103 benchmarks at final checkpoint
- [ ] Run system comparison analysis (System 1 vs 2)
- [ ] Scale to GPT-2 Medium (355M) tier
