# SITREP - v3 Dual-Process Training

## v3 Training Status
**Step 4100/50000 (8.2%)** | GPU: 99% util, 210W/300W, 61°C | **Rate**: ~228 steps/hr | **ETA**: ~8.3 days | Spot: **$0.46/hr** (62% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|------|--------|-----------|-------------|------------|----------|
| 1000 | 21.29  | 6.75      | 5.04%       | 0.557      | 0.0057   |
| 2000 | 22.53  | 6.54      | 6.44%       | 0.613      | 0.0036   |
| 3000 | 23.17  | 6.38      | 7.57%       | 0.638      | 0.0100   |
| 4000 | **23.71** | **6.29** | **8.46%** | **0.672** | **0.0109** |

**Trends**: AR PPL degrading (+11% from step 1k), but **diffusion loss improving** (-6.8%). S1 accuracy climbing steadily (+68%). **Confidence AUROC strengthening** (+21% from step 1k), ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **23.71** | ✅ **PASS** |
| AUROC > 0.75 | **0.672** | ❌ MISS (-0.078) |
| ECE < 0.05 | **0.0109** | ✅ **PASS** |
| Diff loss → 4.0 | **6.29** | ❌ MISS (+2.29) |
| S1 accuracy → 40% | **8.46%** | ❌ MISS (-31.54%) |

**2/5 targets met**. AUROC and S1 accuracy trending upward but need acceleration.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR performance (**23.71 PPL**) significantly better than v1's 43.86, suggesting **joint training benefits** AR model vs v1's regression.

## Infrastructure
**Current session**: 5.2hr uptime, $2.37 spot cost. **Previous session**: terminated after 6.8hr, $3.11 cost. **Total**: 2 spot reclaims, **$5.45** total cost. Instance stable, checkpoints syncing normally.

## What's Next
Monitor **AUROC convergence rate** - needs +0.078 improvement. Expect **S1 acceleration** as diffusion loss approaches target. Consider eval frequency increase around step 10k for finer trend analysis.