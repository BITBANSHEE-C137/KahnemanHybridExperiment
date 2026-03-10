# v3 Training SITREP

## v3 Training Status
**Step 31k/50k (62%)** | L4 GPU @ 100% util, 70W | **~300 steps/hr** | ETA: ~2.6 days | Spot: **$0.46/hr** (53% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 24k  | 29.53  | 4.31     | 25.2%  | 0.862 | 0.0055 |
| 25k  | 29.48  | 4.08     | 26.5%  | 0.861 | 0.0042 |
| 26k  | 29.58  | 4.02     | 27.7%  | 0.864 | 0.0063 |
| 27k  | 29.55  | 4.32     | 24.6%  | 0.866 | 0.0109 |
| 28k  | 29.40  | 4.51     | 23.8%  | 0.865 | 0.0068 |
| 29k  | 29.36  | 4.27     | 25.5%  | 0.867 | 0.0118 |
| 30k  | 29.16  | 4.34     | 24.6%  | 0.868 | 0.0046 |
| **31k** | **28.95** | **4.47** | **23.3%** | **0.871** | **0.0031** |

**Trends**: AR PPL improving steadily (-0.6 since 24k). **AUROC climbing** to 0.871. ECE volatile but **excellent at 0.003**. S1 accuracy **regressing** from 27.7% peak. Diff loss noisy around 4.3.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.95** | ✅ **BEAT** |
| AUROC > 0.75 | **0.871** | ✅ **BEAT** |
| ECE < 0.05 | **0.003** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.47** | ❌ 0.47 over |
| S1 accuracy → 40% | **23.3%** | ❌ 16.7pp short |

**3/5 targets met**. AR performance **exceeds v1 baseline** already. Confidence calibration **exceptional**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
v3 current AR PPL (**28.95**) already **beats v1 WikiText** (43.86) and **matches GPT-2**.

## Infrastructure
Current: g6.2xlarge (L4) running **12.1hrs** stable. **19 spot reclaims** cost $25.52 total vs $43.30 on-demand. Recent instability 3/9 evening (10+ reclaims in 4hrs) now resolved. **Cost efficiency: 53%**.

## What's Next
**19k steps remaining** (~2.6 days). Focus: **S1 accuracy recovery** - trending down from 27.7% peak. Diff loss needs **0.5 reduction** to hit target. After completion: comprehensive v1/v2 comparison, confidence head analysis for production deployment.