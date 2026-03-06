# v2 Training SITREP

## v2 Training Status
Step **31,900/50,000** (63.8% complete). A10G @ **98% util**, 196W/300W, 55°C. Rate: ~400 steps/hr. **ETA: 1.9 days**. Current spot: **$0.45/hr** (62.8% savings vs on-demand). Total cost: **$21.25**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 24k  | 30.98  | 4.46      | 24.3%   | 0.863 | 0.005 |
| 25k  | 31.22  | 4.20      | 27.6%   | 0.860 | 0.012 |
| 26k  | 31.46  | 4.06      | 28.0%   | 0.863 | 0.018 |
| 27k  | 31.46  | 4.48      | 24.4%   | 0.862 | 0.009 |
| 28k  | 31.32  | 3.95      | 28.2%   | 0.872 | 0.007 |
| 29k  | 31.43  | 4.21      | 27.7%   | 0.860 | 0.022 |
| 30k  | 31.68  | 4.08      | 28.1%   | 0.864 | 0.023 |
| 31k  | **31.60** | **4.49** | **24.5%** | **0.862** | **0.014** |

**Trends:** AR PPL stable ~31.5 (good). Diff loss volatile 3.95-4.49. S1 accuracy oscillating 24-28%, **no clear progress**. AUROC solid ~0.86. ECE erratic but generally acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.6** | ✅ **MET** |
| AUROC > 0.75 | **0.862** | ✅ **MET** |
| ECE < 0.05 | **0.014** | ✅ **MET** |
| Diff loss → 4.0 | **4.49** | ❌ **12% over** |
| S1 accuracy → 40% | **24.5%** | ❌ **39% short** |

**3/5 targets met**. S1 accuracy stalled, diff loss regressing.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (31.6) significantly better than v1 WikiText (43.86)**, approaching GPT-2 baseline (29.07).

## Infrastructure
**13 spot sessions**, 21 interruptions. Current session: 4.9hr uptime, no reclaims. Historical avg: **$0.45/hr spot rate**. Total runtime cost: $21.25 vs $32.53 on-demand. Checkpoints syncing normally.

## What's Next
18.1k steps remaining (~1.9 days). Monitor S1 accuracy plateau - may need LR adjustment or curriculum change. Post-v2: benchmark suite, v1 vs v2 head-to-head, confidence calibration deep-dive. **S1 regression is concerning**.