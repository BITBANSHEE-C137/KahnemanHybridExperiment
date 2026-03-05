# v2 Training SITREP

## v2 Training Status
**Step 13,700 / 50,000** (27.4% complete)  
GPU: 100% util, A10G @ 200W/300W, 52°C, 16.6GB/23GB VRAM  
Rate: ~4.5 steps/min based on recent trajectory  
**ETA: ~5.5 days** to completion  
Spot cost: **$0.42/hr** (57.7% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 6000 | 26.44  | 5.12      | 17.5%  | 0.830 | 0.005 |
| 7000 | 27.12  | 5.13      | 17.9%  | 0.833 | 0.008 |
| 8000 | 27.58  | **4.65**  | 21.1%  | 0.845 | 0.007 |
| 9000 | 28.06  | 5.02      | 18.9%  | 0.843 | 0.006 |
| 10000| 28.39  | **4.37**  | **25.1%** | **0.850** | **0.004** |
| 11000| 28.91  | **4.19**  | **26.0%** | **0.857** | 0.005 |
| 12000| 29.35  | 4.34      | 25.6%  | 0.852 | 0.009 |
| 13000| **30.50** | 4.40   | 25.5%  | 0.852 | **0.012** |

**⚠️ AR PPL degrading** (26→30, +15%). **ECE worsening** (0.004→0.012, 3x increase). Diffusion loss improved significantly. S1 accuracy plateaued ~25%.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.5** | ✅ |
| AUROC > 0.75 | **0.85** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.40** | 🔶 (improving) |
| S1 accuracy → 40% | **25.5%** | ❌ (stalled) |

**3/5 targets met**. Diffusion loss trending toward target. S1 accuracy stalled well below target.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v2 AR performance **worse** than v1 final. S1 performance similar to v1.

## Infrastructure
**9 spot sessions**, 8 reclaims in ~24hrs. Frequent interruptions on g5.2xlarge in us-east-1b.  
Switched to g5.xlarge in us-east-1f - **more stable**.  
Total cost: **$9.54** (9 sessions). Current session: 1.7hrs uptime, stable.

## What's Next
Monitor **AR PPL regression** - may need LR adjustment or different training balance.  
S1 accuracy **plateau concerning** - investigate data mixing or loss weighting.  
After completion: comprehensive v1 vs v2 benchmarks, confidence calibration analysis.