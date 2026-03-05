# v2 Training SITREP

## v2 Training Status
**Step 18,800/50,000 (37.6%)** | A10G @ 98% util, 203W/300W, 52°C | **~312 steps/hr** | ETA: ~4.2 days | Spot: **$0.44/hr** (64% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 11000 | 28.91 | 4.19 | 26.0% | 0.857 | 0.005 |
| 12000 | 29.35 | 4.34 | 25.6% | 0.852 | 0.009 |
| 13000 | 30.50 | 4.40 | 25.5% | 0.852 | 0.012 |
| 14000 | 30.34 | 4.31 | 26.0% | 0.853 | 0.011 |
| 15000 | 31.05 | 4.33 | 26.1% | 0.852 | 0.014 |
| 16000 | 30.79 | 4.13 | 26.8% | 0.860 | 0.007 |
| 17000 | 30.70 | 4.52 | 23.7% | 0.860 | 0.007 |
| **18000** | **30.77** | **4.03** | **27.2%** | **0.869** | **0.006** |

**Concerning trends**: AR PPL plateauing at ~30-31. S1 accuracy volatile (23.7% → 27.2%). AUROC improving slowly. Diffusion loss converging to target.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.77** | ✅ **Met** |
| AUROC > 0.75 | **0.869** | ✅ **Met** |
| ECE < 0.05 | **0.006** | ✅ **Met** |
| Diff loss → 4.0 | **4.03** | ✅ **Near target** |
| S1 accuracy → 40% | **27.2%** | ❌ **67% of target** |

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (30.77) already better than v1 WikiText (43.86)** but worse than GPT-2 baseline.

## Infrastructure
**10 spot sessions, 9 reclaims** | Total cost: **$12.67** (64% savings) | Current session: 6.3hrs uptime, no interruptions | Multiple AZ hops (us-east-1b→a→f) suggest capacity constraints

## What's Next
**Critical**: S1 accuracy stagnant at 27% vs 40% target. Monitor next 5k steps for breakthrough. If plateaued, consider S1 loss weight adjustment. Post-completion: comprehensive v1/v2 benchmarks, confidence calibration analysis.