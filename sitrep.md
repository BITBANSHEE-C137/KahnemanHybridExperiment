# v3 Training SITREP

## v3 Training Status
**Step 11,600/50,000 (23.2%)** • GPU: **98% util**, A10G @ 53°C • Rate: ~14 hrs elapsed • **ETA: ~47 hrs** • Spot cost: **$0.46/hr** (62% savings) • **$9.60 total**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 4000 | 23.71 | 6.29 | 8.5% | 0.672 | 0.011 |
| 7000 | 25.48 | 5.87 | 10.6% | 0.739 | 0.009 |
| 10000 | 27.55 | 4.98 | 19.0% | 0.828 | 0.005 |
| **11000** | **27.85** | **4.43** | **22.0%** | **0.853** | **0.010** |

**Trends**: AR PPL **degrading** (+4.1 over 7k steps). Diffusion loss **improving rapidly** (-1.86). S1 accuracy **accelerating** (+13.5pp). AUROC **strong upward trend** (+0.18). ECE **volatile but low**.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **27.85** | ✅ **MET** |
| AUROC | > 0.75 | **0.853** | ✅ **MET** |
| ECE | < 0.05 | **0.010** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.43** | 🔄 **CLOSE** |
| S1 Acc | → 40% | **22.0%** | 🔄 **PROGRESS** |

**3/5 targets met**. Diffusion loss **0.43 above target**. S1 accuracy **18pp below target** but trending well.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26% (PPL 1.46), WikiText 43.86, S1 loss 4.12  
GPT-2: LAMBADA 95.08%, WikiText 29.07  
Current v3 AR PPL (**27.85**) already **beats v1 WikiText** (43.86) and approaching GPT-2 baseline.

## Infrastructure
**Spot stability**: 2 sessions, **1 reclaim** after 6.8hrs (step 1000). Current instance **14.2hrs uptime**, no issues. **$6.49 current session cost**. VRAM: 16.2/23GB (70%).

## What's Next
**39k steps remaining** (~47hrs). Expect diffusion loss to reach 4.0 by step ~15k. S1 accuracy growth rate suggests **35-38%** at completion. **Monitor AR PPL degradation** - may need LR adjustment if exceeds 35.