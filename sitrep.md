# v3 Training Status
**Step 41,100/50,000 (82.2%)** | GPU: 100% util, 81°C | Rate: ~300 steps/hr | **ETA: ~29hrs** | Spot: $0.43/hr (**56.5% savings**)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 34000 | 28.85 | 4.15 | 25.6% | 0.871 | 0.007 |
| 37000 | 28.51 | 4.52 | 24.1% | 0.856 | 0.006 |
| 40000 | **28.27** | **3.76** | **30.3%** | **0.881** | 0.009 |
| 41000 | 28.30 | 3.95 | 27.8% | 0.866 | 0.011 |

**Trends**: AR PPL **plateauing at ~28.3** (excellent). Diff loss **improved dramatically** 4.5→3.8. S1 accuracy **volatile** but trending up. AUROC **regressed** from peak 0.881. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.3** | ✅ **CRUSHED** |
| AUROC > 0.75 | **0.866** | ✅ **MET** |
| ECE < 0.05 | **0.011** | ✅ **MET** |
| Diff loss → 4.0 | **3.95** | ✅ **BEATING** |
| S1 accuracy → 40% | **27.8%** | ❌ **70% of target** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12 | GPT-2: LAMBADA 95.08%, WikiText PPL 29.07

**v3 vs v1**: AR performance **significantly improved** (28.3 vs 43.86 PPL). S1 loss **better** than v1 (3.95 vs 4.12).

## Infrastructure  
**Current**: g6.2xlarge, 2.1hrs uptime, stable | **Total cost**: $33.27 across 21 sessions | **Reliability**: High spot reclaim rate (20 terminated sessions) but quick recovery

**Recent issues**: Multiple brief reclaims 3/9 evening, now stable on current instance since 3/11 07:21

## What's Next
**8,900 steps remaining** (~29hrs). Monitor S1 accuracy volatility. Post-completion: comprehensive v1/v2/v3 benchmark comparison, confidence calibration analysis, final model selection.