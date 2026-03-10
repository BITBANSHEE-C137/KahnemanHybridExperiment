# v3 Training SITREP

## v3 Training Status
**Step 27,800/50,000 (55.6%)** | GPU: **100% util** @ 80°C | Rate: ~1.2 steps/sec | **ETA: ~5.1 hours** | Spot: **$0.46/hr** (53.3% savings)

Current g6.2xlarge instance stable for 6.6h, no recent interruptions.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 20000 | 29.22  | 4.235     | 26.8%  | 0.857 | 0.005 |
| 22000 | 29.70  | **3.945** | 28.3%  | **0.876** | 0.004 |
| 25000 | 29.48  | 4.079     | 26.5%  | 0.861 | 0.004 |
| **27000** | **29.55** | **4.316** | **24.6%** | **0.866** | **0.011** |

⚠️ **Regressions**: S1 accuracy down 4.2% from peak (28.3→24.6%), diffusion loss trending upward. ECE doubled since step 25k.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.55** | ✅ |
| AUROC > 0.75 | **0.866** | ✅ |
| ECE < 0.05 | **0.011** | ✅ |
| Diff Loss → 4.0 | **4.316** | ❌ (+8%) |
| S1 Acc → 40% | **24.6%** | ❌ (39% short) |

**3/5 targets met**. S1 accuracy severely underperforming; diffusion loss unstable.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL

Current AR performance **32% better** than v1 (29.55 vs 43.86 PPL). S1 performance **regressing** vs v1 final.

## Infrastructure
**Total cost: $23.04** across 19 spot sessions. **53% savings** vs on-demand.

Recent instability 3/9 evening (7 reclaims in 3h) resolved. Current g6.2xlarge stable since 3/10 04:25 UTC.

## What's Next
Monitor S1 accuracy regression - may need hyperparameter adjustment. Diffusion loss volatility concerning for target achievement. Complete v3 training, then benchmark against v1/v2 baselines.