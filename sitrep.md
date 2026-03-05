## v2 Training Status
**Step 26k/50k (52%)** on g5.2xlarge spot. GPU at **100% util**, 196W/300W, 52°C. Rate ~2.98 steps/min. **ETA: ~13.4 hours**. Current spot rate $0.45/hr (**63% savings** vs on-demand). Projected total cost **$14.18**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 19k  | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20k  | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21k  | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22k  | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23k  | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24k  | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25k  | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012 |
| 26k  | **31.46** | 4.06   | **28.0%** | 0.863 | **0.018** |

**Trends:** AR PPL slowly climbing (~0.6 points). S1 accuracy improved 3.5pp since step 20k. **ECE degrading** - jumped to 0.018. AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **31.46** | ✅ |
| AUROC | > 0.75 | **0.863** | ✅ |
| ECE | < 0.05 | **0.018** | ✅ |
| Diff Loss | → 4.0 | **4.06** | ✅ |
| S1 Accuracy | → 40% | **28.0%** | ❌ |

**3/5 targets met**. S1 accuracy **12pp short** of target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v2 AR PPL (**31.46**) significantly **better than v1** (43.86). Diff loss tracking well vs v1's 4.12.

## Infrastructure
**12 spot sessions**, 10 spot interruptions in 48hrs. Current session stable 2.6hrs. Total cost **$17.66** across sessions. Recent stability in us-east-1a after bouncing between AZs.

## What's Next
v2 completion in ~13hrs. **Priority: S1 accuracy plateau** - investigate if joint training is hindering S1 performance vs pure diffusion. Post-completion: comprehensive v2 benchmarks, confidence calibration analysis, v1 vs v2 head-to-head comparison.