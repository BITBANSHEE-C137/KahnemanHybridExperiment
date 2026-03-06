# v2 Training SITREP

## v2 Training Status
**Step 28,200/50,000** (56.4% complete). A10G @ **100% GPU util**, 192W/300W, 54°C. VRAM: 16.6GB/23GB used. Training rate ~31.5 steps/min. **ETA: ~11.5 hours**. Current spot rate: **$0.45/hr** (62.9% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25000 | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012 |
| 26000 | 31.46  | 4.06      | 28.0%  | 0.863 | 0.018 |
| 27000 | 31.46  | 4.48      | 24.4%  | 0.862 | 0.009 |
| 28000 | 31.32  | **3.95**  | **28.2%** | **0.872** | 0.007 |

**Trending:** AR PPL stagnating around 31. Diffusion loss **improving** (3.95 latest). S1 accuracy volatile but **trending up**. AUROC **strong upward trend** to 0.872. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.32** | ✅ **MET** |
| AUROC > 0.75 | **0.872** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **3.95** | ✅ **MET** |
| S1 accuracy → 40% | **28.2%** | ❌ **Missing** |

**4/5 targets met.** S1 accuracy needs **+11.8pp** improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. **Current v2 AR performance slightly worse** than v1 (31.32 vs ~27 PPL implied). Diffusion loss **improving toward v1 baseline**. S1 token accuracy progress **encouraging** from joint training.

## Infrastructure
**13 spot sessions**, $19.18 total cost. **Current session stable** (27min uptime). Recent history shows **frequent reclaims** (12 previous sessions). Cost efficiency: **62.9% savings** vs on-demand. No current issues, sync/training running normally.

## What's Next
**22k steps remaining** (~11.5hr). Focus: **S1 accuracy breakthrough** to 40%. Post-completion: v2 benchmarks, v1 comparison, confidence calibration analysis. Monitor for spot reclaims.