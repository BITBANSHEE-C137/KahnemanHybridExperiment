## v3 Training Status
**COMPLETE** - 50k/50k steps (100%). GPU idle (0% util, 16W), training finished. Final rate ~1.64 steps/sec. Total runtime: 8.5h active training. Current spot: **$0.46/hr** (52.6% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 28.14  | 4.196     | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.404     | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.159     | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.943     | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.883     | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.192     | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | 4.407     | 24.9%  | 0.867 | 0.012 |
| **50000** | **27.99** | **4.163** | **26.5%** | **0.871** | **0.012** |

**Trends:** AR PPL stable ~28, slight improvement to 27.99. Diff loss volatile (3.88-4.41), no clear convergence. S1 accuracy peaked at 29.3% (step 47k), regressed. AUROC/ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **27.99** | ✅ **MET** |
| AUROC | > 0.75 | **0.871** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.163** | ⚠️ **CLOSE** |
| S1 Accuracy | → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met.** S1 accuracy significantly below target. Diff loss close but unstable.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v3 shows:** AR improved (27.99 vs 43.86 WikiText-equiv), confidence calibration excellent (ECE 0.012), but S1 accuracy concerning at 26.5% vs ~67% improvement target from v1's 4.12 loss.

## Infrastructure
**22 spot sessions**, **$40.27 total cost** (vs $94.44 on-demand). Major instability 3/9-3/10: 15 reclaims in 5 hours due to spot market chaos. Stable since 3/11 on current g6.2xlarge. **9.4h uptime**, sync running, checkpoints healthy (1.5GB).

## What's Next
**Training complete.** Run v3 benchmarks (LAMBADA, WikiText-103), compare vs v1 baselines. **Priority:** Investigate S1 accuracy regression - may need architectural changes or longer diffusion training for v4.