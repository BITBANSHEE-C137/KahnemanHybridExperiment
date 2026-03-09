# v3 Training SITREP

## v3 Training Status
**Step 8300/50000** (16.6% complete) | GPU: **100% util**, 201W/300W, 57°C | **458 steps/hr** rate | ETA: **90.9 hrs** | Spot cost: **$0.46/hr** (62% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.0%   | 0.557 | 0.006 |
| 4000 | 23.71  | 6.29      | 8.5%   | 0.672 | 0.011 |
| 7000 | 25.48  | 5.87      | 10.6%  | 0.739 | 0.009 |
| 8000 | **26.29** | **5.60** | **12.6%** | **0.785** | **0.008** |

**Trends:** AR PPL slowly degrading (+23% from start), diffusion loss improving (-17%), S1 accuracy climbing (+150%), AUROC strong upward trend (+41%). ECE stable <0.01.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **26.29** | ✅ |
| AUROC > 0.75 | **0.785** | ✅ |
| ECE < 0.05 | **0.008** | ✅ |
| Diff loss → 4.0 | **5.60** | 🟡 (40% to target) |
| S1 accuracy → 40% | **12.6%** | 🔴 (32% remaining) |

**3/5 targets met.** S1 accuracy lagging significantly behind target pace.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**PPL 26.29**) already superior to v1 WikiText baseline and approaching pretrained GPT-2 (PPL 29.07). S1 system showing early learning signs.

## Infrastructure
**Current session:** 10.2h uptime, spot stable at $0.46/hr. **Previous session:** 6.8h (reclaimed), cost $3.11. **Total cost:** $7.74 across 2 sessions. VRAM: 16.2GB/23GB used. Checkpoints syncing normally.

## What's Next
Monitor S1 accuracy trajectory - needs **3x improvement** to hit 40% target. If diffusion loss plateaus above 4.5, consider learning rate adjustment. Current AUROC momentum suggests confidence head performing well.