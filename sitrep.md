# SITREP v3 Training Status

## v3 Training Status
**Just started - Step 0/50K (0%)**. A10G idle at setup, 60W power draw, 2.1GB VRAM loaded. Trainer processes running, sync active. **ETA: Unknown** until first training steps complete. Current spot rate **$0.464/hr** (61.7% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 43k  | 29.96  | 3.93      | 29.2%   | 0.868 | 0.020 |
| 44k  | 29.96  | **4.37**  | **25.4%** | 0.865 | 0.016 |
| 45k  | 29.80  | 3.86      | 29.3%   | 0.875 | 0.016 |
| 46k  | 29.74  | 4.15      | 26.2%   | 0.865 | **0.011** |
| 47k  | 29.72  | **4.61**  | **22.7%** | **0.855** | 0.011 |
| 48k  | 29.72  | **4.73**  | **21.9%** | 0.858 | 0.012 |
| 49k  | 29.64  | 4.24      | 25.4%   | 0.865 | **0.010** |
| 50k  | 29.65  | **4.70**  | **22.0%** | 0.863 | **0.009** |

🔴 **Diffusion loss regressing** (3.93→4.70). S1 accuracy **declining trend** (29.2%→22.0%). AUROC **dropping** from peak 0.875. ECE improving but at cost of calibration accuracy.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **29.65** | ✅ |
| AUROC  | > 0.75 | **0.863** | ✅ |
| ECE    | < 0.05 | **0.009** | ✅ |
| Diff Loss | → 4.0 | **4.70** | 🔴 |
| S1 Accuracy | → 40% | **22.0%** | 🔴 |

**3/5 targets met**. Diffusion and S1 performance deteriorating in final stretch.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc (PPL 1.46), WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance **superior** (29.65 vs 43.86 PPL). S1 token accuracy severely lagging baseline expectations.

## Infrastructure
Single g5.2xlarge spot (us-east-1a), **8min uptime**, $0.06 cost. No reclaims. Stable 61.7% savings rate. Instance fresh for v3 restart.

## What's Next
**Critical**: Investigate S1 accuracy collapse and diffusion instability in final 7K steps. Consider earlier checkpoint (45k) for deployment. Priority: S1 head analysis and potential learning rate adjustment for next training cycle.