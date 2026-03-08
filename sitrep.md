# v3 Training SITREP

## v3 Training Status
**STOPPED** - Step **0/50000** (0.0%). GPU idle at 19% VRAM utilization. Instance running but trainer appears stalled. Spot rate: **$0.46/hr** (62% savings vs on-demand). Current session cost: **$0.06**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 43000 | 29.96  | 3.93      | 29.2%   | 0.868 | 0.020 |
| 44000 | 29.96  | **4.37**  | **25.4%** | 0.865 | 0.016 |
| 45000 | 29.80  | 3.86      | 29.3%   | 0.875 | 0.016 |
| 46000 | 29.74  | 4.15      | 26.2%   | 0.865 | **0.011** |
| 47000 | 29.72  | **4.61**  | **22.7%** | **0.855** | 0.011 |
| 48000 | 29.72  | **4.73**  | **21.9%** | 0.858 | 0.012 |
| 49000 | 29.64  | 4.24      | 25.4%   | 0.865 | **0.010** |
| 50000 | 29.65  | **4.70**  | **22.0%** | 0.863 | **0.009** |

**Trends:** AR PPL stable ~29.7. **Diffusion loss degrading** (3.93→4.70). **S1 accuracy declining** severely (29.2%→22.0%). AUROC volatile but **trending down** (0.868→0.863). ECE **improving** (0.020→0.009).

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.65** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.009** | ✅ **MET** |
| Diff loss → 4.0 | **4.70** | ❌ **MISS** (+18%) |
| S1 accuracy → 40% | **22.0%** | ❌ **MISS** (-45%) |

**3/5 targets met**. Diffusion and S1 performance **severely degraded**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR PPL (**29.65**) beats v1 WikiText baseline. S1 token accuracy (**22.0%**) far below expected joint training performance.

## Infrastructure
2 spot sessions, **1 reclaim** after 9min (session 1). Current session: **7.4min** uptime. Total cost: **$0.10**. Spot pricing stable at $0.46/hr.

## What's Next
**CRITICAL:** Debug trainer stall - step count stuck at 0 despite running process. Investigate S1 accuracy collapse and diffusion loss regression. Consider checkpoint rollback to step 45000 before performance cliff.