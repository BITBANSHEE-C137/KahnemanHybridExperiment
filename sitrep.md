# v3 Training SITREP - Step 28k

## v3 Training Status
**Progress:** 28k/50k steps (56%) | **GPU:** 100% util L4 @ 81°C | **Rate:** ~110 steps/hr | **ETA:** ~8.3 days | **Spot cost:** $0.46/hr (53% savings) | **Total cost:** $23.23

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|--------|-----------|-------------|-------|-----|
| 21k  | 29.94  | 4.26      | 26.8%       | 0.856 | 0.012 |
| 22k  | 29.70  | 3.95      | 28.3%       | 0.876 | 0.004 |
| 23k  | 29.57  | 4.19      | 26.1%       | 0.861 | 0.006 |
| 24k  | 29.53  | 4.31      | 25.2%       | 0.862 | 0.005 |
| 25k  | 29.48  | 4.08      | 26.5%       | 0.861 | 0.004 |
| 26k  | 29.58  | 4.02      | 27.7%       | 0.864 | 0.006 |
| 27k  | 29.55  | 4.32      | 24.6%       | 0.866 | 0.011 |
| **28k** | **29.40** | **4.51** | **23.8%** | **0.865** | **0.007** |

**Trends:** AR PPL plateaued ~29.5. **Diffusion loss trending up** (4.0→4.5). **S1 accuracy declining** (27.7%→23.8%). Confidence metrics stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.4** | ✅ Met |
| AUROC > 0.75 | **0.865** | ✅ Met |
| ECE < 0.05 | **0.007** | ✅ Met |
| Diff loss → 4.0 | **4.51** | ❌ Regressing |
| S1 accuracy → 40% | **23.8%** | ❌ Far below |

**Status:** 3/5 targets met. Diffusion & S1 underperforming.

## v1 Benchmark Baseline  
v1 final: LAMBADA 94.26%, PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. Current AR PPL **29.4 vs 43.86** (33% better than v1). S1 struggling at 23.8% vs target 40%.

## Infrastructure
**19 spot sessions** across g5/g6 instances. Heavy reclaim activity Mar 9 (~12 interruptions). Current g6.2xlarge stable 7hrs. **$23.23 total cost** vs $43.39 on-demand. Some checkpoint step inconsistencies indicate restart overhead.

## What's Next
**Immediate concerns:** Diffusion loss regression & S1 accuracy decline need investigation. Consider LR schedule adjustment. After v3 completion: comprehensive v1/v2/v3 benchmark comparison, confidence head analysis, potential architecture tweaks for S1 performance.