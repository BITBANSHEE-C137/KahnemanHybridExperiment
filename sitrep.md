# v3 Training SITREP

## v3 Training Status
**Step 19,000/50,000 (38.0% complete)** | GPU: 100% util, 208W/300W, 52°C | **23.2 hrs elapsed** | Rate: ~0.82 steps/min | **ETA: ~15.5 days** | Spot cost: **$10.58** (62.3% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 12000 | 28.12 | 4.31 | 25.0% | 0.853 | 0.007 |
| 15000 | 28.64 | 4.50 | 23.7% | **0.864** | 0.005 |
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.008 |
| **19000** | **29.21** | **4.39** | **22.1%** | **0.866** | **0.011** |

**Trends:** AR perplexity **degrading** (+1.09 since step 12k). S1 accuracy **declining** (-2.9pp). AUROC **improving** (+0.013). ECE **volatile** but acceptable. Diffusion loss stable around 4.4.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.21** | ✅ **MET** |
| AUROC > 0.75 | **0.866** | ✅ **MET** |
| ECE < 0.05 | **0.011** | ✅ **MET** |
| Diff loss → 4.0 | **4.39** | ❌ Need -0.39 |
| S1 accuracy → 40% | **22.1%** | ❌ Need +17.9pp |

**3/5 targets met.** S1 accuracy **severely underperforming** vs 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR PPL (29.21) significantly better than v1 baseline (43.86)** but **S1 performance (22.1%) concerning** vs v1's equivalent.

## Infrastructure
**Current:** g5.2xlarge spot (23h uptime) | **Total cost: $13.65** across 2 sessions | **1 spot reclaim** on 2026-03-08 | A10G running efficiently (70% VRAM, 208W) | Checkpoints syncing normally

## What's Next
**Concerning S1 regression** - investigate if joint training methodology causing interference. Monitor AR/S1 loss balance. Consider S1 loss weighting adjustment. After v2: benchmark comparison critical given current S1 underperformance.