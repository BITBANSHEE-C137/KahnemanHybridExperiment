# v3 Training SITREP - Step 31.6K

## v3 Training Status
**Progress:** 31,600/50,000 steps (**63.2%** complete)  
**GPU:** L4 at **99%** utilization, 72W power, 81°C  
**Rate:** ~1.57 steps/min (based on runtime)  
**ETA:** ~19.5 hours remaining  
**Spot Cost:** $0.46/hr (**53.2%** savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 24000| 29.53  | 4.31      | 25.2%  | 0.862 | 0.0055 |
| 26000| 29.58  | 4.02      | 27.7%  | 0.864 | 0.0063 |
| 28000| 29.40  | 4.51      | 23.8%  | 0.865 | 0.0068 |
| 30000| 29.16  | 4.34      | 24.6%  | 0.868 | 0.0046 |
| **31000**| **28.95** | **4.47** | **23.3%** | **0.871** | **0.0031** |

**Trends:** AR perplexity steadily improving (**-2%** over 7K steps). AUROC climbing well. S1 accuracy volatile, concerning **4-point drop** since 26K. ECE excellent and improving.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.95** | ✅ **PASS** |
| AUROC > 0.75 | **0.871** | ✅ **PASS** |
| ECE < 0.05 | **0.0031** | ✅ **PASS** |
| Diff loss → 4.0 | **4.47** | 🟡 Close (need -0.47) |
| S1 accuracy → 40% | **23.3%** | ❌ **FAIL** (-16.7pp) |

**3/5 targets met.** S1 accuracy severely underperforming and regressing.

## v1 Benchmark Baseline
v1 final metrics: LAMBADA 94.26%, WikiText-103 PPL 43.86, S1 loss 4.12  
Current v3: AR PPL **28.95** (34% better than v1's 43.86), S1 performance struggling vs v1's strong diffusion results.

## Infrastructure
**Current:** g6.2xlarge (L4), 13h uptime, stable  
**History:** **19 sessions**, heavy spot reclaims Mar 9 (8 interruptions in 4hrs)  
**Total Cost:** $26.02 across all sessions  
**Reliability:** Much improved since switching to g6.2xlarge

## What's Next
Focus on **S1 token accuracy regression** - consider learning rate adjustment or loss rebalancing. Diffusion loss approaching target. Strong AR performance suggests model capacity isn't the issue.