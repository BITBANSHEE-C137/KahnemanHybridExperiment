# v2 Training SITREP

## v2 Training Status
**Step 26,400/50,000 (52.8%)** | A10G @ 100% util, 195W/300W, 52°C | **1,600 steps/3.1hrs** avg rate | ETA: **~47 hours** | Spot: **$0.45/hr** (63% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 26000 | **31.46** | 4.06 | 28.0% | 0.863 | **0.018** |
| 25000 | 31.22 | 4.20 | 27.6% | 0.860 | 0.012 |
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | 0.005 |
| 23000 | 31.03 | 4.03 | 27.9% | 0.864 | 0.010 |

**Trends:** AR PPL stable ~31. **S1 accuracy climbing** (24% → 28%). AUROC strong at 0.863. **ECE degrading** (0.005 → 0.018) - confidence calibration regressing.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.46** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.018** | ✅ **MET** |
| Diff loss → 4.0 | **4.06** | ⚠️ **CLOSE** |
| S1 accuracy → 40% | **28.0%** | ❌ **MISSING** |

**3/5 targets met.** S1 accuracy trending up but needs +12pp. Diffusion loss nearly converged.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07
**v2 AR PPL (31.46) significantly better than v1 WikiText (43.86)** - joint training improving, not regressing.

## Infrastructure
**12 spot sessions, 11 reclaims** in 2 days. Current session stable 3.1hrs (us-east-1a). Total cost: **$17.88** vs $38.42 on-demand. Most reclaims under 3hrs - need longer-lived instances or checkpointing every 30min.

## What's Next
S1 accuracy **critical path** - need 28% → 40% in remaining 23.6k steps. Monitor confidence calibration drift. After completion: comprehensive v1/v2 benchmarks, confidence head ablations.