# v2 Training SITREP

## v2 Training Status
**Step 30,700/50,000** (61.4%) | **GPU:** 100% util, A10G @ 197W/300W, 54°C | **Rate:** ~400 steps/hr | **ETA:** ~48h | **Spot cost:** $0.45/hr (62.8% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 23k  | 31.03  | 4.03      | 27.9%   | 0.864 | 0.010 |
| 25k  | 31.22  | 4.20      | 27.6%   | 0.860 | 0.012 |
| 27k  | 31.46  | 4.48      | 24.4%   | 0.862 | 0.009 |
| 29k  | 31.43  | 4.21      | 27.7%   | 0.860 | 0.022 |
| **30k** | **31.68** | **4.08** | **28.1%** | **0.864** | **0.023** |

**Trends:** AR PPL stable ~31-32 (good). Diffusion loss volatile 4.0-4.5. S1 accuracy oscillating 24-28%. AUROC plateaued ~0.86. ECE degrading 0.01→0.023.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **31.68** | ✅ **PASS** |
| AUROC | > 0.75 | **0.864** | ✅ **PASS** |
| ECE | < 0.05 | **0.023** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.08** | 🟡 **Near target** |
| S1 Accuracy | → 40% | **28.1%** | ❌ **MISS** (-12pp) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (31.68) significantly better than v1 WikiText (43.86).**

## Infrastructure
**13 spot sessions**, **$20.53 total cost**. Current session: 3.5h uptime, $1.55 cost. **Spot reclaim history:** 12 interruptions across us-east-1a/b/f zones. Aggressive cost optimization working - 63% savings maintained.

## What's Next
**ETA:** Step 50k in ~48h. Priority: **S1 accuracy regression** needs investigation - stuck at 28% vs 40% target. Post-completion: v2 benchmarks, confidence calibration analysis, v1/v2 head-to-head on LAMBADA/WikiText.