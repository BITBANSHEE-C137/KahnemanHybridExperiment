# v2 Training SITREP

## v2 Training Status
**Step 19,200/50,000 (38.4%)** • A10G @ 99% util, 203W/300W, 52°C • **Rate: ~62 steps/hr** • ETA: **~20.5 days** • Spot cost: **$0.44/hr** (64% savings) • Total: **$12.93**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 12000 | 29.35  | 4.34      | 25.6%   | 0.852 | 0.0093 |
| 15000 | 31.05  | 4.33      | 26.1%   | 0.852 | 0.0139 |
| 17000 | 30.70  | 4.52      | 23.7%   | 0.860 | 0.0074 |
| 18000 | 30.77  | 4.03      | 27.2%   | 0.869 | 0.0060 |
| **19000** | **30.81** | **4.31** | **24.5%** | **0.860** | **0.0073** |

**Trends:** AR PPL plateaued ~30-31. **AUROC improving** (+0.008 since 12k). ECE excellent. **S1 accuracy volatile** (23.7%-27.2%). Diffusion loss unstable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **30.81** | ✅ **MET** |
| AUROC | > 0.75 | **0.860** | ✅ **MET** |
| ECE | < 0.05 | **0.007** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.31** | 🔄 **CLOSE** |
| S1 Acc | → 40% | **24.5%** | ❌ **BEHIND** |

**3/5 targets met.** S1 accuracy **16pp below target**, concerning volatility.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.81) better than v1 WikiText (43.86)** but worse than GPT-2. S1 performance tracking behind v1's final state.

## Infrastructure
**Current:** g5.2xlarge us-east-1f, 6.8h uptime. **10 sessions total** with **multiple spot reclaims** (sessions 2-9 lasted 0.7-2.9h each). **Cost discipline good:** $12.93 vs $53.40 on-demand. Frequent interruptions causing training instability.

## What's Next
**Critical:** Address S1 accuracy volatility and push toward 40% target. Monitor diffusion loss convergence to 4.0. After v2 completes: comprehensive v1 vs v2 LAMBADA/WikiText benchmarks, confidence calibration analysis. **Consider reserved instances** to reduce spot interruptions affecting S1 training stability.