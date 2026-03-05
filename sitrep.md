# v2 Training SITREP

## v2 Training Status
**Step 25,600/50,000** (51.2% complete). GPU: **97% util**, 194W/300W, 52°C, 16.6GB/23GB VRAM. Rate: ~11 steps/min. **ETA: ~37 hours**. Spot: **$0.45/hr** (63% savings vs on-demand $1.21/hr).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25000 | **31.22** | **4.20** | **27.6%** | **0.860** | **0.012** |

**Trends**: AR PPL plateauing ~31 (good). S1 accuracy volatile 20-28%. AUROC stable ~0.86. **Diffusion loss erratic** - concerning variance.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.22** | ✅ **Met** |
| AUROC > 0.75 | **0.860** | ✅ **Met** |
| ECE < 0.05 | **0.012** | ✅ **Met** |
| Diff Loss → 4.0 | **4.20** | 🔶 **Close** |
| S1 Acc → 40% | **27.6%** | ❌ **Behind** |

**3/5 targets met**. S1 accuracy **13pts below target**. Diffusion loss close but unstable.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (31.22) better than v1 WikiText**. S1 performance regressing from v1 baseline.

## Infrastructure
**12 spot reclaims** over 2.1 days. Current session: 2.1hrs uptime, us-east-1a. Total cost: **$17.39** ($14.19 projected). Aggressive spot hopping across AZs maintaining training continuity. **No checkpoint losses**.

## What's Next
**~37 hours to completion**. Watch diffusion loss convergence and S1 accuracy recovery. Post-completion: v2 benchmarks, v1 vs v2 head-to-head, confidence calibration deep dive. **S1 target unlikely without intervention**.