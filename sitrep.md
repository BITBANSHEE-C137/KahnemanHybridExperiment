# v3 Training SITREP

## v3 Training Status
**Step 31,900 / 50,000 (63.8%)**  
GPU: NVIDIA L4 at **100% util**, 73W/72W limit, 74°C, 16.6GB/23GB VRAM  
Rate: ~166 steps/hr | ETA: **4.5 days**  
Spot: **$0.46/hr** (53% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.0055 |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.0063 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.0068 |
| 30000 | 29.16  | 4.34      | 24.6%  | 0.868 | 0.0046 |
| **31000** | **28.95** | **4.47** | **23.3%** | **0.871** | **0.0031** |

**Trends:** AR PPL **improving steadily** (-2% over 7k steps). Diffusion loss volatile around 4.3-4.5. S1 accuracy **regressing** from 27.7% peak. AUROC **climbing consistently** (+1% since step 24k). ECE **excellent** and stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.95** | ✅ **MET** |
| AUROC > 0.75 | **0.871** | ✅ **MET** |  
| ECE < 0.05 | **0.003** | ✅ **MET** |
| Diff loss → 4.0 | **4.47** | ❌ Miss by 0.47 |
| S1 accuracy → 40% | **23.3%** | ❌ Miss by 16.7pp |

**3/5 targets met.** Diffusion loss stuck above target. S1 accuracy concerning regression.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**v3 currently:** AR PPL **28.95 < 43.86** (34% better than v1), but diffusion training may be hurting S1 performance vs v1's 4.12 loss equivalent.

## Infrastructure  
**Current:** g6.2xlarge, us-east-1a, 13.6hr uptime  
**Total cost:** $26.21 across 19 sessions (excessive spot reclaims)  
**Spot history:** 18 interruptions since step 20k, mostly g5/g6 switches in us-east-1b  
**Issue:** Frequent reclaims causing training inefficiency - consider reserved capacity

## What's Next
**18.1k steps remaining** (~4.5 days). Monitor S1 accuracy regression closely. After completion: comprehensive v2 vs v1 benchmarks, confidence calibration analysis, investigate diffusion-AR interference effects. Consider spot strategy optimization for future runs.