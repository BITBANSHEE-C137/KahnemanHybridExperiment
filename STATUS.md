# Project Status — Dual-Process Language Model

**Last updated:** 2026-03-07 (v3 pre-flight)

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

## v2 Training: COMPLETE

GPT-2 Small (124M parameters), 50,000 steps on OpenWebText. λ_diff increased from 1.0 to 2.0 to rebalance gradient contribution toward diffusion. Trained March 4–7, 2026 across 15 spot instances with 31 reclamation recoveries. Fleet capacity set to 0, all instances terminated.

### Final Metrics (Step 50,000)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AR Perplexity | 29.65 | < 40 | **Met** — 32% improvement over v1 (43.86→29.65) |
| Confidence AUROC | 0.863 | > 0.75 | **Met** |
| Confidence ECE | 0.009 | < 0.05 | **Met** |
| Diffusion Loss | 4.70 | < 4.0 | 83% — 17% over target |
| S1 Token Accuracy | 22.0% | > 40% | 55% — regressed from v1 (28.7%) |

**3 of 5 targets met.** AR perplexity improved significantly. Diffusion loss regressed vs v1 (4.13→4.70) despite λ_diff=2.0. S1 accuracy collapsed — the higher diffusion weight did not help and may have hurt.

### Cost Summary (v2)

| Metric | Value |
|--------|-------|
| Total cost (v2) | $31.44 |
| Spot instances used | 15 |
| Reclamation events | 31 |
| Savings vs on-demand | 62% |
| Budget cap | $50 |

### Checkpoints

All v2 checkpoints saved to S3 (`v2/step_48000.pt` through `v2/step_50000.pt`, ~1.4 GiB each). Full eval metrics for all 50 steps in `eval_metrics/v2/`.

## v3 Training: PRE-FLIGHT

GPT-2 Small (124M parameters), 50,000 steps on OpenWebText. `diff_loss_weight` reduced from 2.0 (v2) to 1.3, seeking better balance between AR and diffusion objectives. New diagnostics: per-loss gradient norm logging and routing efficiency metrics at confidence thresholds.

### Changes from v2

| Parameter | v2 | v3 | Rationale |
|-----------|----|----|-----------|
| `diff_loss_weight` | 2.0 | 1.3 | v2's aggressive weighting hurt both S1 accuracy and diffusion loss |
| `log_gradient_norms` | — | true | Per-loss gradient norm logging at eval steps |
| `log_routing_efficiency` | — | true | Coverage/accuracy curves at confidence thresholds |
| Post-training | Manual | Automated | 9-step sequence: benchmarks, report, S3 sync, Telegram, fleet shutdown |

### Key Questions

- Does `diff_loss_weight=1.3` (between v1's 1.0 and v2's 2.0) find a better tradeoff?
- Can S1 accuracy recover from v2's regression (22.0%) toward v1's 28.7%?
- Do gradient norms reveal the objective interference mechanism?

### Infrastructure

- Checkpoints: `checkpoints/v3/` (S3), eval metrics: `eval_metrics/v3/`
- Cost ledger: fresh (v2 archived to `cost_ledger_v2.json`)
- AMI: `ami-0544093f9b5424470` (v2 snapshot, code updated via `git pull` on boot)
- `--fresh_start` removed from bootstrap — spot recovery resumes from checkpoint

## Infrastructure

> Full details in [INFRASTRUCTURE.md](INFRASTRUCTURE.md) — spot recovery, bootstrap, dashboards, cost analysis.

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance | Spot fleet | g5.2xlarge / g6.xlarge, capacity=0 (idle) |
| AMI | `ami-0544093f9b5424470` | Post-v2 snapshot, launch template v20 |
| EBS root volume | ~100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme` — runtime data |
| EBS static data | Tagged `ml-lab-static-data` | Preprocessed data, one volume per AZ |
| Bootstrap | Ready | 18-step autonomous spot recovery |
| Web dashboard | Active | [train.bitbanshee.com](https://train.bitbanshee.com) |
| Telegram | Active | Spot reclaims, budget alerts, sitreps |
| Cost controls | Active | $50 budget cap + $0.75/hr spot ceiling |
| Sync daemon | Active | S3 artifact sync (60s interval) |

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
- [x] v2 training launched with λ_diff=2.0 rebalancing
- [x] Clean AMI — no baked secrets, all fetched from Secrets Manager at boot
- [x] Telegram integration — spot reclaims, budget alerts, sitreps, price ceiling
- [x] Cost controls — $50 budget cap + $0.75/hr spot ceiling with auto-shutdown
- [x] Dashboard UX refresh — merged Instance & GPU card, reorganized Infrastructure card
- [x] Cost projection formula — rate-based remaining time instead of linear extrapolation
- [x] Persistent EBS volumes for preprocessed static data
- [x] IAM role expanded — EBS attach/detach/describe permissions
- [x] Cron env var propagation fixed — Telegram, Spot Token passed inline
- [x] LAMBADA + WikiText-103 benchmarks complete (v1)
- [x] Complete v2 training (50,000 steps) — v2 DONE
- [x] Fleet shut down, AMI snapshotted (`ami-0544093f9b5424470`), launch template updated to v20
- [x] v3 pre-flight: removed `--fresh_start` from bootstrap, fixed Lambda CONFIG_SUMMARY, archived v2 cost ledger
- [x] v3 prep: `diff_loss_weight` 2.0→1.3, gradient norm logging, routing efficiency metrics, automated post-training sequence

## Next Steps

> See [README.md — Planned Work](README.md#planned-work) for the full research roadmap.

- [ ] Launch v3 training (fleet capacity → 1)
- [ ] Monitor gradient norm ratio (AR vs diffusion) to validate `diff_loss_weight=1.3`
- [ ] v1 vs v2 vs v3 comparison — S1 accuracy, diffusion loss, AR PPL tradeoff
- [ ] Confidence head analysis — escalation rates, S1 vs S2 quality per difficulty tier
- [ ] Implement confidence scoring fix (accumulate during unmasking, not post-hoc)
- [ ] Scale to GPT-2 Medium (355M) tier
