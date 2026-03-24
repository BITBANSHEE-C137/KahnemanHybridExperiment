# SITREP v4 Training Status

## v4 Training Status
**Step:** 39,600/75,000 (**52.8%** complete)  
**GPU:** A10G @ **100%** utilization, 200W/300W, 56°C, 16.6GB/23GB VRAM  
**Rate:** ~4.4 steps/min, **ETA:** ~8.1 hours  
**Spot Cost:** $0.44/hr (**63.8%** savings), **$3.74** current session

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 36000 | 31.11  | 4.200     | 29.9%  | 0.864 | 0.021 |
| 37000 | 30.10  | 4.337     | 27.7%  | 0.854 | 0.020 |
| 38000 | 29.43  | 4.382     | 27.7%  | 0.856 | 0.016 |
| 39000 | 29.17  | 4.082     | 30.5%  | 0.857 | 0.008 |
| **39500** | **29.10** | **4.366** | **26.9%** | **0.855** | **0.016** |

**Trends:** AR PPL steadily improving (**-6.5%** since step 36k). Diff loss volatile but trending toward target. S1 accuracy **regressing** (-3.6pp from peak). AUROC stable but below target. ECE showing good calibration improvement.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.10** | ✅ **PASS** |
| AUROC  | > 0.75 | **0.855** | ✅ **PASS** |
| ECE    | < 0.05 | **0.016** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.37** | ⚠️ **CLOSE** |
| S1 Accuracy | → 40% | **26.9%** | ❌ **BEHIND** |

**3/5 targets met.** S1 accuracy **concerning regression** from 30.5% peak.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v4 AR performance already exceeds v1** (29.1 vs 43.86 PPL)

## Infrastructure
**Current:** g5.2xlarge us-east-1e, **8.5h** uptime  
**Spot History:** 73 sessions, **frequent** interruptions in us-east-1f  
**Total Cost:** $52.16 across all sessions  
**Stability:** Current session **stable**, no recent reclaims

## What's Next
S1 accuracy regression needs **immediate analysis** - may require confidence head rebalancing. On track to complete v4 by end of week. Post-completion: comprehensive v1 vs v4 benchmarks, confidence calibration deep dive.