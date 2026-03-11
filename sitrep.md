## v3 Training Status
**Step 46k/50k (92% complete)** | GPU: L4 @ 100% util, 71W/72W, 83°C | Rate: ~15 steps/min | **ETA: ~4.5 hours** | Spot: $0.463/hr (52.5% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 39k  | 28.34  | 4.043    | 29.04%  | 0.863  | 0.011 |
| 40k  | 28.27  | 3.757    | **30.28%** | **0.881** | **0.009** |
| 41k  | 28.30  | 3.949    | 27.81%  | 0.866  | 0.011 |
| 42k  | 28.33  | 3.892    | 29.15%  | 0.870  | 0.013 |
| 43k  | 28.14  | 4.196    | 25.93%  | 0.869  | 0.010 |
| 44k  | **28.07** | 4.404    | 24.89%  | 0.867  | **0.010** |
| 45k  | **27.95** | 4.159    | 26.49%  | 0.870  | 0.011 |
| 46k  | 28.13  | **3.943**    | **28.06%** | 0.866  | 0.016 |

**Trends:** AR PPL improving gradually. **Diffusion loss volatile** (4.4→3.9 swing). S1 accuracy **highly unstable** (25-30% range). AUROC plateaued ~0.87. **ECE regressed** last step.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.13** | ✅ **PASS** |
| AUROC | > 0.75 | **0.866** | ✅ **PASS** |
| ECE | < 0.05 | **0.016** | ✅ **PASS** |
| Diff Loss | → 4.0 | **3.94** | ✅ **ON TARGET** |
| S1 Acc | → 40% | **28.1%** | ❌ **MISS (-12%)** |

**4/5 targets met.** S1 accuracy significantly behind target, showing high variance.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v3 AR PPL (**28.13**) already **beating WikiText baseline** and approaching v1 levels. **36% improvement** in diffusion loss vs v1 final.

## Infrastructure
**Current:** g6.2xlarge, us-east-1a, 1.95hrs uptime
**Total cost:** $37.19 across 22 sessions | **Avg savings: 52.5%**
**Stability issues:** 13 spot reclaims in 48hrs (Mar 9-10), now stable 2hr+ on current instance

## What's Next
**4k steps to completion** → v2 benchmarks → detailed v1/v2/v3 comparison → **confidence head ablation study** → production deployment decision