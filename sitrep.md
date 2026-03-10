# v3 Training SITREP

## v3 Training Status
**Progress:** 33,300/50,000 steps (**66.6%** complete)  
**GPU:** L4 at **99% util**, 72W, 82°C, 16.6/23GB VRAM  
**Rate:** ~4.9 steps/min (based on 16.7hr runtime)  
**ETA:** ~56 hours remaining  
**Spot Cost:** $0.46/hr (**53% savings** vs on-demand), $20.42 projected total

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 26000 | 29.58 | 4.02 | 27.7% | 0.864 | 0.006 |
| 27000 | 29.55 | 4.32 | 24.6% | 0.866 | 0.011 |
| 28000 | 29.40 | 4.51 | 23.8% | 0.865 | 0.007 |
| 29000 | 29.36 | 4.27 | 25.5% | 0.867 | 0.012 |
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.005 |
| 31000 | 28.95 | 4.47 | 23.3% | 0.871 | 0.003 |
| 32000 | 29.04 | 4.35 | 24.2% | 0.865 | 0.009 |
| **33000** | **28.93** | **4.09** | **26.6%** | **0.861** | **0.009** |

**Trends:** AR perplexity steadily improving (**-2.3% since 26k**). Diffusion loss volatile but trending down. S1 accuracy recovered from 28k dip. **AUROC regression** from 0.871→0.861 concerning.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.93** | ✅ **PASS** |
| AUROC | > 0.75 | **0.861** | ✅ **PASS** |
| ECE | < 0.05 | **0.009** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.09** | ⚠️ **Close** |
| S1 Accuracy | → 40% | **26.6%** | ❌ **FAIL** |

**3/5 targets met.** S1 accuracy significantly below target. AUROC declining trend needs monitoring.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07  
**Current v3 AR performance on track** to match/exceed v1. S1 task still underperforming baseline.

## Infrastructure
**Current:** g6.2xlarge (L4), 16.1hrs uptime, $7.33 spent  
**History:** 19 spot sessions, **frequent reclaims** in early training (11 interruptions on 3/9). Stabilized on current instance since 3/10 04:25 UTC.  
**Total cost:** $27.36 across all sessions

## What's Next
Continue to 50k steps. **Monitor AUROC regression** - if continues, investigate confidence head training dynamics. Expect S1 accuracy plateau unless architectural changes made. Post-50k: comprehensive v1/v2/v3 benchmark comparison.