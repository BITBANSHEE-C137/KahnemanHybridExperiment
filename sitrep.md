# v3 Training SITREP

## v3 Training Status
**Step 8700/50000** (17.4% complete) | A10G @ **100% util**, 201W/300W, 57°C | **16.1GB/23GB VRAM** used  
Rate: ~4.3 steps/min | **ETA: ~6.7 days** | Spot cost: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 1000 | 21.29  | 6.75     | 5.0%   | 0.557  | 0.006 |
| 4000 | 23.71  | 6.29     | 8.5%   | 0.672  | 0.011 |
| 6000 | 24.85  | 6.08     | 9.9%   | 0.719  | 0.012 |
| 8000 | **26.29** | **5.60** | **12.6%** | **0.785** | **0.008** |

**Trends:** AR PPL **regressing** (+23% from step 1k). Diffusion loss improving steadily (-17%). S1 accuracy **climbing** (+150%). AUROC **strong upward** trend (+41%).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **26.29** | ✅ |
| AUROC | > 0.75 | **0.785** | ✅ |
| ECE | < 0.05 | **0.008** | ✅ |
| Diff Loss | → 4.0 | **5.60** | 🔄 (improving) |
| S1 Accuracy | → 40% | **12.6%** | 🔄 (climbing) |

**3/5 targets met.** Diffusion loss needs **-29%** improvement. S1 accuracy needs **+217%** gain.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (26.29) already beating v1 (43.86) by 40%** - promising early signal.

## Infrastructure
**Current:** g5.2xlarge spot (10.7hr uptime) | **Total cost: $7.97** across 2 sessions  
**History:** 1 spot reclaim at step 1000 (6.8hr session, $3.11) → current session stable  
**Projected:** $27.8 total vs $73.5 on-demand (**62% savings**)

## What's Next
Strong confidence calibration progress (AUROC cleared target early). **Watch AR PPL trend** - needs investigation if regression continues. S1 accuracy climbing but needs acceleration. After completion: comprehensive v1 vs v3 analysis focusing on joint training trade-offs.