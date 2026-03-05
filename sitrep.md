# v2 Training SITREP

## v2 Training Status
**Step 21,700 / 50,000 (43.4%)** | **GPU**: A10G @ 97% util, 196W/300W, 54°C | **Rate**: ~12 steps/min | **ETA**: ~39h | **Spot cost**: $0.45/hr (63% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 14000 | 30.34  | 4.31      | 25.96% | 0.853 | 0.011 |
| 16000 | 30.79  | 4.13      | 26.82% | 0.860 | 0.007 |
| 18000 | 30.77  | 4.03      | 27.23% | 0.869 | 0.006 |
| 20000 | 30.92  | 4.75      | 21.31% | 0.851 | 0.007 |
| 21000 | 30.88  | 4.85      | 20.67% | 0.851 | 0.007 |

**Trends**: AR PPL **plateaued ~30.8**. Diff loss **regressing** (4.03→4.85). **S1 accuracy declining** sharply (27%→21%). AUROC stable. ECE excellent.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.88** | ✅ |
| AUROC > 0.75 | **0.851** | ✅ |
| ECE < 0.05 | **0.007** | ✅ |
| Diff loss → 4.0 | **4.85** | ❌ (regressing) |
| S1 accuracy → 40% | **20.67%** | ❌ (declining) |

**3/5 targets met**. Concerning **S1 degradation**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

v2 **AR quality similar to v1** (PPL ~31 vs 44). **S1 performance poor** vs v1's 67% improvement.

## Infrastructure
**Current**: g5.2xlarge spot, 1.8h uptime, $0.81 session cost
**History**: 11 sessions, 10 spot reclaims, **$15.13 total cost** vs $43.5 on-demand
**Stability**: Frequent interruptions but auto-resume working. Latest checkpoint: step_21000.pt (1.5GB)

## What's Next
**Immediate**: Investigate S1 accuracy collapse - potential overfitting or hyperparameter issue
**Post-completion**: v2 benchmarks, confidence calibration analysis, v1 comparison on LAMBADA/WikiText