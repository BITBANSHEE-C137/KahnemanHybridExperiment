## v2 Training Status
**Step 24,800/50,000 (49.6%)** running on g5.2xlarge A10G at **100% GPU util**. Current rate ~7 steps/min, **ETA ~60 hours**. Spot cost: **$0.45/hr (63% savings)**, projected total **$14.12** vs $38.19 on-demand.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 17000 | 30.70  | 4.52      | 23.7%   | 0.860 | 0.0074 |
| 18000 | 30.77  | **4.03**  | **27.2%** | **0.869** | **0.0060** |
| 19000 | 30.81  | 4.31      | 24.5%   | 0.860 | 0.0073 |
| 20000 | 30.92  | **4.75**  | 21.3%   | 0.851 | 0.0072 |
| 21000 | 30.88  | **4.85**  | 20.7%   | 0.851 | 0.0075 |
| 22000 | 30.95  | 4.19      | **27.5%** | 0.858 | 0.0096 |
| 23000 | 31.03  | **4.03**  | **27.9%** | 0.864 | 0.0095 |
| 24000 | 30.98  | 4.46      | 24.3%   | 0.863 | **0.0050** |

**Trends**: AR PPL stagnant ~31. Diff loss volatile (4.0-4.9 range). S1 accuracy peaked at step 23000 but regressed. AUROC stable ~0.86. ECE improving.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.98** | ✅ |
| AUROC > 0.75 | **0.863** | ✅ |
| ECE < 0.05 | **0.0050** | ✅ |
| Diff loss → 4.0 | **4.46** | ❌ (volatile) |
| S1 accuracy → 40% | **24.3%** | ❌ (regressing) |

**3/5 targets met**. Diffusion loss unstable, S1 accuracy concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v2 AR performance (PPL 30.98) **better than v1** (43.86). S1 accuracy at 24% vs target 40% - significant gap remains.

## Infrastructure
**12 spot sessions**, 63% savings vs on-demand. Current instance: 1.1hr uptime, no interruptions. Previous sessions show **frequent spot reclaims** (21 interruptions), but training resilient with checkpoint recovery.

## What's Next
**25,200 steps remaining** (~60hrs). Monitor S1 accuracy regression and diff loss volatility. After completion: comprehensive v2 benchmarks, confidence calibration analysis, and detailed v1 vs v2 comparison on all eval suites.