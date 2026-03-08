## v3 Training Status
**Step 2900/50000** (5.8% complete). GPU at **100% util**, 204W/300W, 59°C. Current rate ~400 steps/hr. **ETA: ~120 hours**. Running g5.2xlarge spot at **$0.46/hr** (62% savings vs on-demand). Total cost: **$4.76**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75     | 5.0%   | 0.557 | 0.0057 |
| 2000 | **22.53** | **6.54** | **6.4%** | **0.613** | **0.0036** |

**Trends:** AR perplexity **regressing** (+1.24). Diffusion loss improving (-0.21). S1 accuracy climbing (+1.4pp). Confidence AUROC improving (+0.056), ECE improving (-0.002).

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **22.53** | ✅ **MET** |
| AUROC > 0.75 | **0.613** | ❌ **MISS** (-0.137) |
| ECE < 0.05 | **0.0036** | ✅ **MET** |
| Diff loss → 4.0 | **6.54** | ❌ **MISS** (+2.54) |
| S1 accuracy → 40% | **6.4%** | ❌ **MISS** (-33.6pp) |

**2/5 targets met.** Early in training but diffusion/S1 targets ambitious.

## v1 Benchmark Baseline
v1@50k: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12. Current v3 AR PPL (22.53) **significantly better** than v1 WikiText baseline (43.86) despite early training. S1 accuracy (6.4%) tracking behind v1 trajectory.

## Infrastructure
**2 spot sessions**, 1 reclaim at step 1000. Current instance up **3.7hrs**, stable. Previous session cost $3.11 (6.8hrs), current $1.64. **No recent interruptions**.

## What's Next
Monitor AR perplexity regression - may indicate joint training interference. S1 accuracy climbing slowly but diffusion loss needs aggressive improvement. Next eval checkpoint at step 3000 critical for trend confirmation.