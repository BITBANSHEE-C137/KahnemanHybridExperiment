# v2 Training SITREP

## v2 Training Status
**COMPLETE** - 50k/50k steps (100%). GPU idle post-completion. Current spot: **$0.46/hr** (61.8% savings vs on-demand). Training completed at 05:00 UTC after 11h runtime on current instance.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|--------|-------|
| 43000 | 29.96  | 3.93      | 29.2%  | 0.868  | 0.020 |
| 45000 | 29.80  | 3.86      | 29.3%  | 0.875  | 0.016 |
| 47000 | 29.72  | 4.61      | 22.7%  | 0.855  | 0.011 |
| 49000 | 29.64  | 4.24      | 25.4%  | 0.865  | 0.010 |
| **50000** | **29.65** | **4.70** | **22.0%** | **0.863** | **0.009** |

**Trends**: AR PPL stable ~29.7. Diffusion loss volatile (3.86→4.70), concerning uptick. S1 accuracy degraded from 29%→22%. AUROC stable mid-0.86s. **ECE improving** (0.020→0.009).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.65** | ✅ **MET** |
| AUROC | > 0.75 | **0.863** | ✅ **MET** |
| ECE | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.70** | ❌ **MISS** (+17%) |
| S1 Accuracy | → 40% | **22.0%** | ❌ **MISS** (-45%) |

**3/5 targets met**. Diffusion and S1 performance below expectations.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. v2 shows **32% AR improvement** (43.86→29.65 PPL) but **S1 regressed significantly** vs v1's 67% drop achievement.

## Infrastructure
15 spot sessions, **31 reclaims** across 3 AZs. Total cost: **$31.44** (62% savings). Current instance stable 11h+ (longest: 16h session 13). Checkpoints syncing, 1.5GB final model saved.

## What's Next
**Priority**: v2 benchmarks on LAMBADA/WikiText to quantify AR gains. Investigate diffusion loss volatility and S1 accuracy collapse. Compare confidence calibration improvements (ECE: 0.020→0.009) against v1 baseline.