# v3 Training SITREP

## v3 Training Status
**Step 41,700/50,000 (83.4%)** | GPU: **100% util** L4 @ 71W/72W, 78°C | Rate: ~300 steps/hr | **ETA: 28 hours** | Spot: **$0.43/hr** (56.5% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 34k   | 28.85  | 4.15      | 25.6%  | 0.871 | 0.0069 |
| 36k   | 28.59  | 4.46      | 23.5%  | 0.864 | 0.0109 |
| 38k   | 28.43  | 4.02      | 28.5%  | 0.864 | 0.0092 |
| 40k   | 28.27  | 3.76      | 30.3%  | **0.881** | 0.0094 |
| 41k   | **28.30** | **3.95** | **27.8%** | 0.866 | **0.0105** |

**Trends:** AR PPL plateauing around 28.3. Diffusion loss improving toward target (**3.95→4.0**). S1 accuracy volatile but trending up. **AUROC regression** from 40k peak (0.881→0.866). ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **28.3** | ✅ **MET** |
| AUROC  | > 0.75 | **0.866** | ✅ **MET** |
| ECE    | < 0.05 | **0.0105** | ✅ **MET** |
| Diff Loss | → 4.0 | **3.95** | ✅ **NEAR** |
| S1 Acc | → 40% | **27.8%** | ❌ **BEHIND** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 4.12 loss. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **v3 AR performance significantly better than v1** (28.3 vs 43.86 PPL).

## Infrastructure
**21 spot sessions**, **$33.66 total cost**. Current g6.2xlarge stable 3.1h (longest recent). Heavy spot churn Mar 9 (12 reclaims in 6h). **56.5% cost savings** vs on-demand ($7.37 projected vs $16.94).

## What's Next
8.3k steps remaining (~28h). **Monitor AUROC regression** - may need confidence head tuning. S1 accuracy lagging target. Post-completion: comprehensive v1/v2/v3 benchmark suite, confidence calibration analysis.