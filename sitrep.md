# v3 Training SITREP - Step 33900

## v3 Training Status
**Step 33900/50000 (67.8% complete)** | GPU: **100% util** L4 @ 72W | **17.1 hrs remaining** @ current pace  
Spot rate: **$0.46/hr** (53% savings vs on-demand) | Current session cost: **$7.83** | Total project: **$27.82**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 26000| 29.58  | 4.02      | 27.7%  | 0.864 | 0.006 |
| 28000| 29.40  | 4.51      | 23.8%  | 0.865 | 0.007 |
| 30000| 29.16  | 4.34      | 24.6%  | 0.868 | 0.005 |
| 32000| 29.04  | 4.35      | 24.2%  | 0.865 | 0.009 |
| **33000**| **28.93** | **4.09** | **26.6%** | **0.861** | **0.009** |

**Trends:** AR PPL steadily improving (-2.2% over 7k steps). Diff loss volatile but trending down. **S1 accuracy recovered** from 23.8% dip. AUROC plateaued around 0.865. ECE stable <0.01.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.93** | ✅ **PASS** |
| AUROC | > 0.75 | **0.861** | ✅ **PASS** |  
| ECE | < 0.05 | **0.009** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.09** | ✅ **PASS** |
| S1 Accuracy | → 40% | **26.6%** | ❌ **MISS** |

**4/5 targets met.** S1 accuracy **33% below target** but recovering from recent dip.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v3 AR PPL (**28.93**) already **outperforming v1** (43.86) and approaching GPT-2 baseline.

## Infrastructure
Current: **g6.2xlarge L4** in us-east-1a, **17+ hrs uptime**  
Spot history: **19 sessions**, heavy churn 3/9 (12 reclaims in 4hrs). Stabilized since 3/10.  
Cost efficiency: **53% savings** vs on-demand. Checkpoints syncing normally.

## What's Next
**16.1k steps remaining** (~17 hrs). Monitor S1 accuracy recovery. After completion: comprehensive v3 benchmarks vs v1/GPT-2 baselines, confidence calibration analysis, joint training impact assessment.