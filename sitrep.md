# v3 Training SITREP

## v3 Training Status
**Step 46,300/50,000 (92.6%)** | GPU: **100% util** @ 71W/74°C | Rate: ~300 steps/2.4hrs | **ETA: 7.4hrs** | Spot: **$0.463/hr** (52.5% savings)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 39000 | 28.34  | 4.043     | 29.0%  | 0.863 | 0.0113 |
| 40000 | 28.27  | 3.757     | 30.3%  | **0.881** | 0.0094 |
| 41000 | 28.30  | 3.949     | 27.8%  | 0.866 | 0.0105 |
| 42000 | 28.33  | 3.892     | 29.1%  | 0.870 | 0.0126 |
| 43000 | 28.14  | 4.196     | 25.9%  | 0.869 | 0.0103 |
| 44000 | 28.07  | **4.404** | 24.9%  | 0.867 | 0.0096 |
| 45000 | **27.95** | 4.159     | 26.5%  | 0.870 | 0.0112 |
| 46000 | 28.13  | **3.943** | **28.1%** | 0.866 | **0.0155** |

**Trends:** AR PPL plateaued ~28. Diff loss volatile (3.7-4.4). S1 acc recovering from step 44k dip. **ECE degrading** (0.009→0.015).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40    | **28.13** | ✅ |
| AUROC  | >0.75  | **0.866** | ✅ |
| ECE    | <0.05  | **0.0155** | ✅ |
| Diff Loss | →4.0 | **3.943** | ✅ |
| S1 Acc | →40%  | **28.1%** | ❌ |

**4/5 targets met.** S1 accuracy **12pp below target**.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR performance on-track** (28 vs 44 PPL). S1 loss improved 4%.

## Infrastructure
**22 spot sessions**, $37.38 total cost. Current g6.2xlarge stable **2.5hrs**. Previous session (g6.2xlarge/us-east-1b) ran **9.2hrs** without interruption. **No recent reclaims** - spot market stable.

## What's Next
**3,700 steps remaining** (~7hrs). Monitor **ECE regression** and **S1 accuracy plateau**. Post-completion: comprehensive v1/v2/v3 benchmark suite, confidence calibration deep-dive.