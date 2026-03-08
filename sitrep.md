# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 6600/50000 (13.2%)** | GPU: A10G @ 100% util, 206W/300W, 60°C | **Rate**: ~229 steps/hr | **ETA**: ~8.4 days | Spot: $0.46/hr (**62% savings** vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.006 |
| 2000 | 22.53  | 6.54      | 6.44%  | 0.613 | 0.004 |
| 3000 | 23.17  | 6.38      | 7.57%  | 0.638 | 0.010 |
| 4000 | 23.71  | 6.29      | 8.46%  | 0.672 | 0.011 |
| 5000 | 24.35  | 6.12      | 9.13%  | 0.695 | 0.008 |
| 6000 | **24.85** | **6.08** | **9.86%** | **0.719** | **0.012** |

**Concerning AR degradation**: PPL climbing from 21.3→24.9 (+17%). **Good progress** on AUROC (0.56→0.72) and S1 accuracy doubling. Diffusion loss improving steadily.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **24.85** | ✅ **PASS** |
| AUROC > 0.75 | **0.719** | ❌ **96% there** |
| ECE < 0.05 | **0.012** | ✅ **PASS** |
| Diff Loss → 4.0 | **6.08** | ❌ **Need -34%** |
| S1 Acc → 40% | **9.86%** | ❌ **Need 4x** |

**2/5 targets met**. AUROC very close, but S1 accuracy severely behind target pace.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. **Current v3 AR PPL (24.85) already beating v1 baseline (43.86)** by 43%. Confidence calibration excellent vs v1's untuned state.

## Infrastructure
**Uptime**: 8.2hrs current session | **Total cost**: $6.86 across 2 sessions | **1 spot reclaim** at step 1000 (6.8hr interruption, auto-resumed) | Checkpoints: 4k, 5k, 6k syncing properly

## What's Next
**Priority**: Investigate AR degradation trend - may need LR schedule adjustment or loss weighting. S1 accuracy severely lagging - review tokenization strategy. AUROC within striking distance of target. Continue monitoring spot stability in us-east-1a.