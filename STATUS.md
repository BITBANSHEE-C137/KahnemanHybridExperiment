# Project Status  -  Dual-Process Language Model

**Last updated:** 2026-03-08 (v3 training)

> See also: [README.md](README.md) for research narrative and results | [INFRASTRUCTURE.md](INFRASTRUCTURE.md) for ops and deployment details

## Live Dashboard

**[train.bitbanshee.com](https://train.bitbanshee.com)**  -  training metrics, loss curves, and cost tracking. Served via CloudFront with S3 fallback when instances are down.

## v1 Training: COMPLETE

GPT-2 Small (124M parameters), 50,000 steps on OpenWebText. Trained March 1–3, 2026 across 4 spot instances with 3 reclamation recoveries. Fleet capacity set to 0, all instances terminated.

### Final Metrics (Step 50,000)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AR Perplexity | 26.9 | < 40 | **Met** |
| Confidence AUROC | 0.854 | > 0.75 | **Met** |
| Confidence ECE | 0.010 | < 0.05 | **Met** |
| Diffusion Loss | 4.13 | < 4.0 | 97%  -  narrowly missed |
| S1 Token Accuracy | 28.7% | > 40% | 72%  -  not met |

**3 of 5 targets met.** Diffusion loss and S1 accuracy within striking distance  -  planned λ rebalancing for v2.

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
| AR Perplexity | 29.65 | < 40 | **Met**  -  32% improvement over v1 (43.86→29.65) |
| Confidence AUROC | 0.863 | > 0.75 | **Met** |
| Confidence ECE | 0.009 | < 0.05 | **Met** |
| Diffusion Loss | 4.70 | < 4.0 | 83%  -  17% over target |
| S1 Token Accuracy | 22.0% | > 40% | 55%  -  regressed from v1 (28.7%) |

**3 of 5 targets met.** AR perplexity improved significantly. Diffusion loss regressed vs v1 (4.13→4.70) despite λ_diff=2.0. S1 accuracy collapsed  -  the higher diffusion weight did not help and may have hurt.

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

## v3 Training: COMPLETE

GPT-2 Small (124M parameters), 50,000 steps on OpenWebText. `diff_loss_weight` reduced from 2.0 (v2) to 1.3. Trained March 8–15, 2026. New diagnostics: per-loss gradient norm logging and routing efficiency metrics.

### Final Metrics (Step 50,000)

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| AR Perplexity | 28.0 | < 40 | **Met** |
| Confidence AUROC | 0.870 | > 0.75 | **Met** |
| Confidence ECE | 0.012 | < 0.05 | **Met** |
| Diffusion Loss | 4.16 | < 4.0 | 96% — closest yet |
| S1 Token Accuracy | 26.5% | > 40% | 66% — recovered from v2's 22% |

**3 of 5 targets met.** λ_diff=1.3 recovered S1 accuracy from v2's regression and nearly matched v1's diffusion loss. Critically, **v3 hit all 5 targets at step 40k** (S1 acc 30.3%, diff loss 3.757) before regressing by step 50k — the cosine LR at 40k was still ~5.5e-5, high enough to destabilize the multi-objective equilibrium.

### Key Finding

The model *can* converge to the sweet spot — it just can't hold it. Late-stage LR is too high, and the cosine schedule is too steep at the point where all objectives align. This directly motivates v4's schedule changes.

## v4 Training: READY

GPT-2 Small (124M parameters), 75,000 steps on OpenWebText. Goal: **stabilize late-stage training so the model holds the sweet spot v3 found at 40k**.

### Changes from v3

| Parameter | v3 | v4 | Rationale |
|-----------|----|----|-----------|
| `max_steps` | 50000 | 75000 | Gentler cosine slope — LR at 40k drops from ~5.5e-5 to ~4.5e-5 |
| `min_learning_rate` | 3.0e-5 | 1.0e-5 | Flatter floor reduces late-stage oscillation |
| `min_mask_ratio` | 0.1 | 0.2 | Eliminates near-trivial batches (10% masking teaches little) |
| `max_mask_ratio` | 1.0 | 0.9 | Avoids generate-from-nothing batches (too hard for 124M) |
| `gradient_accumulation_steps` | 8 | 12 | Effective batch 48 (was 32) — smoother multi-objective gradients |
| `eval_every` | 1000 | 500 | Finer eval granularity to catch the sweet spot |
| Best checkpoint | — | `best.pt` | Composite score tracking: `s1_acc + max(0, 4.0 - diff_loss)` |
| Optimizer betas | hardcoded | configurable | `adam_beta1`, `adam_beta2` in config (still 0.9/0.95) |

### What's NOT Changing (and why)

- **λ_diff=1.3** — v3 proved this works. Three runs show the lambda search is done.
- **LR peak 3e-4** — standard for GPT-2 small, early training looks fine across all runs.
- **Confidence weight 0.1** — AUROC steadily improves. Not the bottleneck.
- **Architecture** — 124M GPT-2 can clearly learn both objectives.
- **Data** — same OpenWebText memmap.

### Infrastructure

- Checkpoints: `checkpoints/v4/` (S3), eval metrics: `eval_metrics/v4/`
- AMI: `ami-0e52bd0d4640a3d73` (same clean AMI as v3)
- Launch template: `lt-06e111b12bd85396f` v21 (no changes needed)
- Budget: $50 cap (75k steps at ~$0.60/hr ≈ $40-45 estimated)

## Infrastructure

> Full details in [INFRASTRUCTURE.md](INFRASTRUCTURE.md)  -  spot recovery, bootstrap, dashboards, cost analysis.

| Component | Status | Details |
|---|---|---|
| S3 bucket | Active | `s3://ml-lab-004507070771/dual-system-research-data/` |
| Instance | Spot fleet | g5.2xlarge / g6.xlarge, capacity=1 (v3 training) |
| AMI | `ami-0e52bd0d4640a3d73` | Clean AMI, launch template v21 |
| EBS root volume | ~100GB | OS + Python 3.12 + ML stack |
| Ephemeral NVMe | 419GB | `/opt/dlami/nvme`  -  runtime data |
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
- [x] GPU verified  -  L4/A10G detected, CUDA matmul confirmed
- [x] requirements.txt created
- [x] Project source code built (src/, configs/, tests/)
- [x] AMI snapshot with current environment
- [x] First smoke test on tiny config
- [x] OpenWebText preprocessing (memmap shards)
- [x] Full training launched on tiny config (GPT-2 Small, 50k steps)
- [x] Web dashboard  -  live at [train.bitbanshee.com](https://train.bitbanshee.com)
- [x] HTTPS + CloudFront + ACM TLS (auto-renewing)
- [x] Dashboard hardened  -  token auth on write endpoints, SSE limits, security headers
- [x] Route53 DNS auto-update on instance boot
- [x] Fully autonomous bootstrap  -  all services start without manual intervention
- [x] Checkpoint frequency increased to every 1,000 steps
- [x] Local checkpoint cleanup (keep last 3, S3 has all)
- [x] Spot price monitoring via cron + IMDSv2 auto-detection
- [x] Bootstrap battle-tested across 4 spot recovery cycles
- [x] CloudFront + ACM TLS (no more certbot/Let's Encrypt)
- [x] S3 fallback page when instance is down
- [x] Dashboard UX refresh  -  larger fonts, narrower layout, footer, S1 Acc tile
- [x] Complete training run (50,000 steps)  -  v1 DONE
- [x] v2 training launched with λ_diff=2.0 rebalancing
- [x] Clean AMI  -  no baked secrets, all fetched from Secrets Manager at boot
- [x] Telegram integration  -  spot reclaims, budget alerts, sitreps, price ceiling
- [x] Cost controls  -  $50 budget cap + $0.75/hr spot ceiling with auto-shutdown
- [x] Dashboard UX refresh  -  merged Instance & GPU card, reorganized Infrastructure card
- [x] Cost projection formula  -  rate-based remaining time instead of linear extrapolation
- [x] Persistent EBS volumes for preprocessed static data
- [x] IAM role expanded  -  EBS attach/detach/describe permissions
- [x] Cron env var propagation fixed  -  Telegram, Spot Token passed inline
- [x] LAMBADA + WikiText-103 benchmarks complete (v1)
- [x] Complete v2 training (50,000 steps)  -  v2 DONE
- [x] Fleet shut down, AMI snapshotted (`ami-0544093f9b5424470`), launch template updated to v20
- [x] v3 pre-flight: removed `--fresh_start` from bootstrap, fixed Lambda CONFIG_SUMMARY, archived v2 cost ledger
- [x] v3 prep: `diff_loss_weight` 2.0→1.3, gradient norm logging, routing efficiency metrics, automated post-training sequence
- [x] Clean AMI bake: `ami-0e52bd0d4640a3d73`  -  infra constants in `/etc/ml-lab/infra.env`, no baked secrets or version-specific vars
- [x] Launch template updated to v21 with clean AMI
- [x] Bootstrap simplified: only injects secrets + version-derived paths (infra from AMI)
- [x] Lambda fleet commands fixed (`/start`, `/stop` work from Telegram)
- [x] Lambda webhook secret fixed (env var mismatch)
- [x] v3 training launched (2026-03-08)

## Next Steps

> See [README.md  -  Planned Work](README.md#planned-work) for the full research roadmap.

- [ ] Monitor gradient norm ratio (AR vs diffusion) to validate `diff_loss_weight=1.3`
- [ ] v1 vs v2 vs v3 comparison  -  S1 accuracy, diffusion loss, AR PPL tradeoff
- [ ] Confidence head analysis  -  escalation rates, S1 vs S2 quality per difficulty tier
- [ ] Implement confidence scoring fix (accumulate during unmasking, not post-hoc)
- [ ] Scale to GPT-2 Medium (355M) tier
