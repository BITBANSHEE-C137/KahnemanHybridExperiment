# v2 Training SITREP

## v2 Training Status
**Step 29,000/50,000 (58%)** - A10G @ **99% util**, 194W/300W, 53°C  
Rate: ~6.7 steps/min | **ETA: ~52 hours** | Current spot: **$0.45/hr** (63% savings)  
Projected total cost: **$12.03** vs $32.43 on-demand

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 22000 | 30.95  | 4.19      | 0.275  | 0.858 | 0.010  |
| 24000 | 30.98  | 4.46      | 0.243  | 0.863 | 0.005  |
| 26000 | 31.46  | 4.06      | 0.280  | 0.863 | 0.018  |
| 28000 | 31.32  | 3.95      | 0.282  | **0.872** | 0.007  |
| **29000** | **31.43** | **4.21** | **0.277** | **0.860** | **0.022** |

**Trends:** AR PPL stable ~31. Diff loss volatile (3.95→4.21). AUROC peaked at 28k then regressed. **ECE spiked 3x** - confidence calibration degrading.

## Target Scorecard
- ✅ **AR PPL < 40:** 31.43 (PASS)
- ✅ **AUROC > 0.75:** 0.860 (PASS) 
- ✅ **ECE < 0.05:** 0.022 (PASS, but trending worse)
- ❌ **Diff loss → 4.0:** 4.21 (MISS, unstable)
- ❌ **S1 accuracy → 40%:** 27.7% (MISS, plateaued)

**3/5 targets met.** Diffusion and S1 performance stalling.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v2 AR PPL (31.43) already beats v1 (43.86)** but still trails pretrained GPT-2.

## Infrastructure  
**13 spot sessions, 12 reclaims** - high churn but stable recovery  
Current instance: 1.5hrs uptime, us-east-1b  
Total cost: **$19.63** across 2.5 days of training

## What's Next
After step 50k: Full v2 benchmarks, v1→v2 comparison on LAMBADA/WikiText  
**Priority:** Investigate confidence head calibration regression and diffusion loss instability  
Consider learning rate decay for final 21k steps