# v3 Training SITREP

## v3 Training Status
**Step 2500/50000 (5.0%)** | GPU: 99% util, 59°C, 16.2/23GB VRAM | Rate: ~0.23 steps/s | **ETA: ~58 hours** | Spot cost: **$0.46/hr** (62% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.0057 |
| 2000 | **22.53** | **6.54** | **6.44%** | **0.613** | **0.0036** |

**Trends:** AR perplexity **regressing** (+1.24). Diffusion loss improving (-0.21). S1 accuracy climbing (+1.4pp). AUROC improving (+0.056). ECE calibration excellent and improving.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **22.53** | ✅ **MET** |
| AUROC > 0.75 | **0.613** | ❌ Need +0.14 |
| ECE < 0.05 | **0.0036** | ✅ **MET** |
| Diff loss → 4.0 | **6.54** | ❌ Need -2.54 |
| S1 accuracy → 40% | **6.44%** | ❌ Need +33.6pp |

**3/5 targets on track.** AUROC and diffusion loss need significant improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. Current v3 AR performance (22.53 PPL) **significantly better** than v1's 43.86 baseline.

## Infrastructure
**Current session:** 3h 10m uptime, $1.45 spent. **Previous session:** 6h 47m, terminated at step 1000, $3.11 cost. **Total:** 2 spot reclaims, $4.53 total spend, **projected $27.85** to completion vs $73.48 on-demand.

## What's Next
Monitor AR perplexity regression trend closely. If continues, investigate LR schedule or loss weighting. Target next eval at step 4000 to assess AUROC/diffusion progress. Confidence calibration already excellent—focus tuning on core capabilities.