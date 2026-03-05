# v2 Training SITREP

## v2 Training Status
**Step 20,900/50,000 (41.8%)** - NVIDIA A10G @ **98% GPU util**, 202W/300W, 52°C. Rate: ~400 steps/hr. **ETA: ~18 hours**. Current spot: **$0.44/hr** (63.9% savings vs on-demand). Total run cost: **$13.80**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 13000 | 30.50  | 4.40      | 25.5%  | 0.852 | 0.012 |
| 14000 | 30.34  | 4.31      | 26.0%  | 0.853 | 0.011 |
| 15000 | 31.05  | 4.33      | 26.1%  | 0.852 | 0.014 |
| 16000 | 30.79  | 4.13      | 26.8%  | 0.860 | 0.007 |
| 17000 | 30.70  | 4.52      | 23.7%  | 0.860 | 0.007 |
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20000 | **30.92** | **4.75** | **21.3%** | **0.851** | **0.007** |

**Concerning trends**: S1 accuracy **regressing hard** (27.2% → 21.3%), diffusion loss **spiking** (4.03 → 4.75), AUROC **declining** from peak 0.869. AR PPL stable but not improving.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.92** | ✅ **PASS** |
| AUROC > 0.75 | **0.851** | ✅ **PASS** |
| ECE < 0.05 | **0.007** | ✅ **PASS** |
| Diff loss → 4.0 | **4.75** | ❌ **REGRESSING** |
| S1 accuracy → 40% | **21.3%** | ❌ **FAR BELOW** |

**3/5 targets met**. S1 task severely underperforming, diffusion loss trending wrong direction.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 currently matching v1 AR performance** but **S1 task worse than v1** (21% vs implied ~33% from loss 4.12).

## Infrastructure
**10 spot sessions**, 8 reclaims. Current instance stable 8.8hrs. Mix of g5.xlarge/2xlarge across us-east-1a/b/f. **Excessive churn** - averaging 1 reclaim per 1000 steps. Total cost $13.77 vs $53.33 on-demand.

## What's Next
**Immediate concern**: S1 accuracy collapse needs diagnosis. Consider reducing diffusion loss weight or LR adjustment. After completion: comprehensive v1/v2 benchmark comparison, confidence calibration analysis, S1 task failure investigation.