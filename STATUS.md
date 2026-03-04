# Project Status — Dual-Process Language Model

**Last updated:** 2026-03-03

> See also: [README.md](README.md) for research narrative and results | [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for ops and deployment details

## Live Dashboard

**[train.bitbanshee.com](https://train.bitbanshee.com)** — training metrics, loss curves, and cost tracking. Served via CloudFront with S3 fallback when instances are down.

## v1 Training: COMPLETE

GPT-2 Small (124M parameters), 50,000 steps on OpenWebText. Trained March 1–3, 2026 across 4 spot instances with 3 reclamation recoveries. Fleet capacity set to 0, all instances terminated.

### Final Metrics (Step 50,000)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AR Perplexity | 26.9 | < 40 | **Met** |
| Confidence AUROC | 0.854 | > 0.75 | **Met** |
| Confidence ECE | 0.010 | < 0.05 | **Met** |
| Diffusion Loss | 4.13 | < 4.0 | 97% — narrowly missed |
| S1 Token Accuracy | 28.7% | > 40% | 72% — not met |

**3 of 5 targets met.** Diffusion loss and S1 accuracy within striking distance — planned λ rebalancing for v2.

### Cost Summary

| Metric | Value |
|--------|-------|
| Total cost | $27.62 |
| Spot instances used | 4 |
| Reclamation recoveries | 3 |
| Savings vs on-demand | 63% |

### Checkpoints

All 50 checkpoints saved to S3 (`step_1000.pt` through `step_50000.pt`, ~1.4 GiB each). Available on request.

## Infrastructure

> Full details in [INFRASTRUCTURE.md](INFRASTRUCTURE.md) — spot recovery, bootstrap, dashboards, cost analysis.

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance | Terminated | g5.2xlarge (spot), fleet capacity = 0 |
| EBS root volume | 100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data |
| Bootstrap | Ready | Fully autonomous spot recovery (CloudFront-aware) |
| Web dashboard | Fallback | [train.bitbanshee.com](https://train.bitbanshee.com) — CloudFront + S3 fallback (EC2 offline) |
| DNS | Configured | `train.bitbanshee.com` → CloudFront ALIAS; `origin.train.bitbanshee.com` → EC2 A record |
| Sync daemon | Idle | S3 artifact sync (runs when instance active) |

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
- [x] HTTPS + CloudFront + ACM TLS (auto-renewing)
- [x] Dashboard hardened — token auth on write endpoints, SSE limits, security headers
- [x] Route53 DNS auto-update on instance boot
- [x] Fully autonomous bootstrap — all services start without manual intervention
- [x] Checkpoint frequency increased to every 1,000 steps
- [x] Local checkpoint cleanup (keep last 3, S3 has all)
- [x] Spot price monitoring via cron + IMDSv2 auto-detection
- [x] Bootstrap battle-tested across 4 spot recovery cycles
- [x] CloudFront + ACM TLS (no more certbot/Let's Encrypt)
- [x] S3 fallback page when instance is down
- [x] Dashboard UX refresh — larger fonts, narrower layout, footer, S1 Acc tile
- [x] Complete training run (50,000 steps) — v1 DONE

## Next Steps

> See [README.md — Planned Work](README.md#planned-work) for the full research roadmap.

- [x] Complete training run (50,000 steps) — DONE
- [ ] Run LAMBADA + WikiText-103 benchmarks on final checkpoint
- [ ] Run system comparison analysis (System 1 vs 2)
- [ ] v2 training with rebalanced loss weights
- [ ] Scale to GPT-2 Medium (355M) tier
