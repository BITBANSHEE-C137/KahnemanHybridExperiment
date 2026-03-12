# v3 Training SITREP

## v3 Training Status
**COMPLETE** - Step **50,000/50,000** (100%). Instance idle - trainer offline, sync running. Current A10G GPU: 0% util, 11W/300W, 29°C. Spot rate: **$0.47/hr** (61% savings vs on-demand). **Total cost: $40.35**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867 | 0.012 |
| 50000 | 27.99  | 4.16      | 26.5%  | 0.870 | 0.012 |

**Trends**: AR PPL stable ~28 (good). Diffusion loss volatile 3.88-4.41. S1 accuracy peaked at 29.3% then declined. AUROC stable ~0.87. ECE decent <0.016.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | ❌ **MISSED** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISSED** |

**3/5 targets met**. Diffusion training unstable. S1 performance plateau'd.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR PPL **27.99 vs 43.86** (36% better). S1 performance **26.5% vs baseline inference needed**. Confidence calibration excellent.

## Infrastructure  
**23 sessions, 8 spot reclaims**. Heavy churn 3/9-3/10 with multiple brief sessions. Stabilized on g6.2xlarge instances for final 10k steps. Current session: 19min uptime, no issues.

## What's Next
**Training complete** - ready for v3 benchmarking. Priority: LAMBADA/WikiText eval, v1 vs v3 comparison, confidence head analysis. Need to debug diffusion loss volatility and S1 accuracy plateau for next iteration.