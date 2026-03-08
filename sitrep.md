# ML Ops SITREP - v3 Training

## v3 Training Status
**TRAINING NOT STARTED** - Step 0/50k (0.0%). GPU at **35% utilization** (A10G, 109W/300W, 34°C, 4.4GB/23GB VRAM). Training systems initialized but no forward passes logged. Current spot rate **$0.46/hr** (61.7% savings vs on-demand $1.21/hr). No ETA available.

## Eval Metrics & Trends
Training data shows **completed v3 run** (steps 43k-50k trajectory):

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 43000 | 29.96 | 3.93 | 0.292 | 0.868 | 0.020 |
| 45000 | 29.80 | 3.86 | 0.293 | 0.875 | 0.016 |
| 47000 | 29.72 | 4.61 | 0.227 | 0.855 | 0.011 |
| 49000 | 29.64 | 4.24 | 0.254 | 0.865 | 0.010 |
| 50000 | 29.65 | 4.70 | 0.220 | 0.863 | 0.009 |

**Trends:** AR PPL stabilized ~29.7. Diffusion loss volatile (3.86→4.70). S1 accuracy **regressed severely** (29.2%→22.0%). ECE improving (halved). AUROC stable ~0.86.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.65** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss → 4.0 | **4.70** | ❌ **MISS** (+17.5%) |
| S1 Accuracy → 40% | **22.0%** | ❌ **MISS** (-45%) |

**3/5 targets met.** Diffusion and S1 both significantly underperformed.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. v3 shows **AR improvement** (29.65 vs 43.86 PPL) but **S1 catastrophic regression** (22% vs target 40%).

## Infrastructure
2 spot sessions in us-east-1a. First instance reclaimed after 9min ($0.07). Current session: 7.9min uptime, $0.06 cost. **Total cost: $0.127.** No training interruptions on current instance.

## What's Next
**CRITICAL:** Investigate S1 token accuracy collapse. Current training appears stalled at step 0 despite showing completed trajectory data. Verify trainer state and resume/restart as needed. Priority: diagnose S1 head degradation before continuing.