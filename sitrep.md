# v2 Training SITREP

## v2 Training Status
**Step 35,200/50,000 (70.4%)** | A10G @ **98% util**, 190W/300W, 50°C | **16.6GB/23GB VRAM** | Rate: ~400 steps/hr | **ETA: ~15hrs** | Spot: **$0.45/hr** (63% savings) | Current session: **9hrs uptime**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 28000 | 31.32  | 3.95      | 28.2%  | 0.872 | 0.007 |
| 30000 | 31.68  | 4.08      | 28.1%  | 0.864 | 0.023 |
| 32000 | 31.39  | 3.96      | 28.4%  | 0.871 | 0.013 |
| 34000 | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| **35000** | **30.84** | **4.79** | **21.4%** | **0.855** | **0.011** |

**Trends**: AR PPL steadily improving ✅ | Diff loss regressing ⚠️ | **S1 accuracy declining** 🚨 | AUROC volatile | ECE stable

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.84** | ✅ |
| AUROC > 0.75 | **0.855** | ✅ |
| ECE < 0.05 | **0.011** | ✅ |
| Diff loss → 4.0 | **4.79** | ❌ (regressing) |
| S1 accuracy → 40% | **21.4%** | ❌ (declining) |

**3/5 targets met**. Diffusion and S1 performance concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

v2 AR performance **ahead of v1** (30.84 vs 43.86 PPL). S1 training unstable.

## Infrastructure
**13 spot sessions**, **$23 total cost** vs $32.56 on-demand (29% savings)
Current: 9hrs uptime, no reclaims. Previous: 12 interruptions, avg session 3.2hrs
**Spot stability poor** - frequent reclaims impacting training rhythm

## What's Next
**Critical**: Investigate S1 accuracy collapse and diff loss divergence
After completion: Full v2 benchmarks, confidence calibration analysis, v1→v2 joint training impact study