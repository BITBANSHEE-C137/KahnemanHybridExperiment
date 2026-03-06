# v2 Training SITREP

## v2 Training Status
**Step 28,600/50,000** (57.2% complete). A10G at **100% util**, 192W/300W, 54°C. Current rate ~215 steps/hr. **ETA: 41 hours**. Spot cost **$0.45/hr** (63% savings), projected total **$12.02**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 21000 | 30.88 | 4.85 | 20.7% | 0.851 | 0.0075 |
| 22000 | 30.95 | 4.19 | 27.5% | 0.858 | 0.0096 |
| 23000 | 31.03 | 4.03 | 27.9% | 0.864 | 0.0095 |
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | 0.0050 |
| 25000 | 31.22 | 4.20 | 27.6% | 0.860 | 0.0120 |
| 26000 | 31.46 | 4.06 | 28.0% | 0.863 | 0.0177 |
| 27000 | 31.46 | 4.48 | 24.4% | 0.862 | 0.0095 |
| 28000 | 31.32 | **3.95** | 28.2% | **0.872** | 0.0073 |

**Trends**: AR PPL **plateaued ~31**, diffusion loss volatile but trending down. S1 accuracy stuck in 24-28% range. AUROC **improving** (+0.021 since step 21k). ECE unstable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.32** | ✅ |
| AUROC > 0.75 | **0.872** | ✅ |
| ECE < 0.05 | **0.007** | ✅ |
| Diff loss → 4.0 | **3.95** | ✅ |
| S1 accuracy → 40% | **28.2%** | ❌ |

**4/5 targets met**. S1 accuracy significantly behind target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v2 AR PPL (**31.32**) already **28% better** than v1's WikiText performance. Diffusion loss approaching v1's S1 baseline.

## Infrastructure
**13 spot sessions**, $19.40 total cost. Current instance: 57min uptime, stable. **Multiple reclaims** (sessions 2-12 show frequent interruptions). Longest stable run: 10hrs (session 10). Checkpoint sync active.

## What's Next
Complete v2 training (~41hrs). **Priority**: investigate S1 accuracy plateau - may need learning rate adjustment or loss weighting. Run full v2 benchmarks, compare against v1 baselines, analyze confidence calibration improvements.