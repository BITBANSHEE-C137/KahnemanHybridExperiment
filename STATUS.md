# Project Status — Dual-Process Language Model

**Last updated:** 2026-03-01

> See also: [README.md](README.md) for research narrative and results | [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for ops and deployment details

## Live Dashboard

**[train.bitbanshee.com](https://train.bitbanshee.com)** — real-time training metrics, GPU stats, loss curves, and cost tracking.

## Training Progress

| Metric | Value |
|---|---|
| Current step | ~2,300 / 50,000 (4.6%) |
| Phase | Cosine decay (warmup completed at step 2,000) |
| Instance | g5.2xlarge (NVIDIA A10G, spot) |

**Note:** Steps 100–4,000+ from the initial run were lost across spot terminations before checkpoint frequency was increased. Checkpoint interval is now every 1,000 steps (was 5,000). The eval history below is from the prior run and represents validated training dynamics.

### Eval History

| Step | AR PPL | Diff Loss | S1 Token Acc | Conf Acc | Conf ECE | Conf AUROC | Run |
|------|--------|-----------|-------------|----------|----------|------------|-----|
| 50 | 19,060 | 7.8397 | 3.4% | 96.6% | 0.0499 | 0.467 | 1 |
| 100 | 23,331 | 7.5697 | 3.2% | 96.8% | 0.0037 | 0.502 | 1 |
| 1,000 | 20,575 | 6.7854 | 4.9% | 95.1% | 0.0028 | 0.550 | 2 |
| 2,000 | 21,752 | 6.5495 | 6.5% | 93.5% | 0.0014 | 0.607 | 2 |
| 3,000 | 21,412 | 6.5179 | 7.1% | 92.9% | 0.0057 | 0.628 | 1 |
| 4,000 | 22,406 | 6.2339 | 8.6% | 91.5% | 0.0052 | 0.669 | 1 |

**Trends:** Diffusion loss steadily declining (7.84 → 6.23 over 4k steps). S1 token accuracy 2.5× above random baseline. Confidence AUROC improving linearly (0.47 → 0.67). Step 2,000 eval from current run confirms prior trends reproducing.

## Infrastructure

> Full details in [INFRASTRUCTURE.md](INFRASTRUCTURE.md) — spot recovery, bootstrap, dashboards, cost analysis.

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance type | Active | g5.2xlarge / g6.xlarge (spot fleet) |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data |
| Bootstrap | Autonomous | Fully autonomous spot recovery with TLS cert backup/restore |
| Web dashboard | Live | [train.bitbanshee.com](https://train.bitbanshee.com) — CloudFront + nginx + Flask |
| DNS | Automated | `train.bitbanshee.com` → CloudFront ALIAS; `origin.train.bitbanshee.com` → EC2 A record (bootstrap-managed) |
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
- [x] CloudFront + ACM TLS (no more certbot/Let’s Encrypt)
- [x] S3 fallback page when instance is down
- [x] Dashboard UX refresh — larger fonts, narrower layout, footer, S1 Acc tile

## Next Steps

> See [README.md — Planned Work](README.md#planned-work) for the full research roadmap.

- [ ] Complete training run (50,000 steps)
- [ ] Run LAMBADA + WikiText-103 benchmarks at final checkpoint
- [ ] Run system comparison analysis (System 1 vs 2)
- [ ] Scale to GPT-2 Medium (355M) tier
