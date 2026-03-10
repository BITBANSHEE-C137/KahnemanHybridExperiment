# ML Ops SITREP - v3 Training Status
*2026-03-10 12:00 UTC*

## v3 Training Status
**Step 28,300/50,000 (56.6%)** | GPU: **97%** util, 72W/72W, 81°C | Rate: ~1.8 steps/min | **ETA: 8.4 days** | Spot: **$0.46/hr** (-53% vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 21000| 29.94  | 4.26      | 26.8%   | 0.856 | 0.012 |
| 22000| 29.70  | 3.95      | 28.3%   | **0.876** | 0.004 |
| 23000| 29.57  | 4.19      | 26.1%   | 0.861 | 0.006 |
| 24000| 29.53  | 4.31      | 25.2%   | 0.862 | 0.005 |
| 25000| 29.48  | 4.08      | 26.5%   | 0.861 | 0.004 |
| 26000| 29.58  | 4.02      | 27.7%   | 0.864 | 0.006 |
| 27000| 29.55  | 4.32      | 24.6%   | 0.866 | 0.011 |
| **28000**| **29.40** | **4.51** | **23.8%** | **0.865** | **0.007** |

**Trends**: AR PPL plateaued ~29.5, **S1 accuracy declining** since step 22k. Diff loss unstable. AUROC solid but ECE volatile.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **29.4** | ✅ **PASS** |
| AUROC | > 0.75 | **0.865** | ✅ **PASS** |
| ECE | < 0.05 | **0.007** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.51** | ⚠️ **12% over** |
| S1 Accuracy | → 40% | **23.8%** | ❌ **FAIL** (-40%) |

**Concerns**: S1 performance **regressing badly** - down from 28.3% to 23.8% in 6k steps.

## v1 Benchmark Baseline
v1 final metrics: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: 95.08% LAMBADA, 29.07 WikiText PPL. **Current v3 AR performance ahead of v1** but S1 joint learning failing.

## Infrastructure
Current: g6.2xlarge, 7.5hr uptime, **19 spot reclaims** since start. Total cost: **$23.46** (53% savings). Session stability poor - multiple brief reclaims around step 20k causing training fragmentation.

## What's Next
**Critical**: Investigate S1 accuracy regression - may need learning rate adjustment or loss weighting. Continue monitoring diff loss convergence to 4.0 target. Next eval at step 29k.