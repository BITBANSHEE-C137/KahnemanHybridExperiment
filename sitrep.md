# v2 Training SITREP

## v2 Training Status
**Step 21,200/50,000 (42.4%)** | GPU: **100% util** A10G @ 199W/300W, 54°C | VRAM: 16.6/23.0 GB | Rate: ~76 steps/hr | **ETA: ~15.8 days** | Spot: **$0.45/hr** ($16.18 projected vs $43.63 on-demand, **62.9% savings**)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 14000 | 30.34  | 4.31      | 25.96% | 0.853 | 0.011 |
| 15000 | 31.05  | 4.33      | 26.09% | 0.852 | 0.014 |
| 16000 | 30.79  | 4.13      | 26.82% | 0.860 | 0.007 |
| 17000 | 30.70  | 4.52      | 23.65% | 0.860 | 0.007 |
| 18000 | 30.77  | 4.03      | 27.23% | 0.869 | 0.006 |
| 19000 | 30.81  | 4.31      | 24.46% | 0.860 | 0.007 |
| 20000 | 30.92  | 4.75      | 21.31% | 0.851 | 0.007 |
| 21000 | 30.88  | 4.85      | 20.67% | 0.851 | 0.007 |

**🚨 REGRESSIONS:** S1 accuracy declining (-5.3% from peak), diffusion loss trending up (+0.85 since step 18k). AUROC plateaued after initial gains.

## Target Scorecard
| Target            | Current | Status |
|-------------------|---------|---------|
| AR PPL < 40       | **30.9** | ✅ MET |
| AUROC > 0.75      | **0.851** | ✅ MET |
| ECE < 0.05        | **0.007** | ✅ MET |
| Diff loss -> 4.0  | **4.85** | ❌ (+0.85) |
| S1 accuracy -> 40%| **20.7%** | ❌ (-19.3%) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR performance competitive but S1 struggling vs v1's 4.12 loss.**

## Infrastructure
g5.2xlarge spot (us-east-1b) running **1.31 hrs**, no interruptions. Trainer + sync active, checkpoints current. **Strong 62.9% cost savings** holding.

## What's Next
**Immediate:** Monitor S1 degradation - may need LR adjustment or loss rebalancing. **Post-completion:** Full benchmark suite, confidence calibration analysis, v1/v2 head-to-head comparison on reasoning tasks.