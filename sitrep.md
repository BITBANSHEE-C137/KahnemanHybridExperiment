# v2 Training SITREP - March 5, 2026

## v2 Training Status
**Step 18,000/50,000 (36% complete)** | **GPU: 100% util, 203W/300W, 52°C** | **Rate: ~2.9 steps/min** | **ETA: ~18.5 hours** | **Spot cost: $0.44/hr (64% savings)**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 16000 | 30.79  | 4.13      | 26.8%  | 0.860 | 0.007  |
| 17000 | 30.70  | 4.52      | 23.7%  | 0.860 | 0.007  |
| 18000 | **30.77** | **4.03** | **27.2%** | **0.869** | **0.006** |

**Trends:** AR PPL stable ~31. Diffusion loss volatile but trending toward target. **S1 accuracy improved +3.5% latest step**. AUROC climbing steadily. ECE excellent and improving.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.77** | ✅ **Met** |
| AUROC > 0.75 | **0.869** | ✅ **Met** |
| ECE < 0.05 | **0.006** | ✅ **Met** |
| Diff loss → 4.0 | **4.03** | ✅ **Met** |
| S1 accuracy → 40% | **27.2%** | ❌ **Need +12.8%** |

**3/5 targets met. S1 accuracy is the bottleneck.**

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.77) better than v1 (43.86) but worse than GPT-2 baseline.**

## Infrastructure
**Current:** g5.2xlarge us-east-1f, 5.3h uptime, $2.31 spent
**Total:** 10 sessions, **$12.23 cumulative cost** | **Multiple spot reclaims** (9 interruptions) causing training instability | **Need more stable instance selection**

## What's Next
**Priority:** S1 accuracy optimization - consider loss weighting adjustments. After completion: comprehensive v1 vs v2 benchmarks, confidence calibration analysis, architecture ablations.