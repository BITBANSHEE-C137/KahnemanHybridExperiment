# v2 Training SITREP

## v2 Training Status
**Step 40,200/50,000 (80.4%)** | A10G @ **100% GPU util**, 193W/300W, 53°C | **~245 steps/hr** | ETA: **~40 hours** | Spot: **$0.46/hr** (62.7% savings)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 33000 | 31.29  | 4.23      | 25.4%  | 0.864 | 0.0075 |
| 36000 | 30.69  | 4.30      | 24.8%  | 0.863 | 0.0100 |
| 38000 | 30.44  | 4.28      | 26.7%  | 0.865 | 0.0042 |
| 39000 | 30.41  | **3.80**  | **30.7%** | 0.863 | 0.0068 |
| 40000 | **30.21** | 4.56   | 23.2%  | 0.857 | 0.0072 |

**Trends**: AR PPL improving steadily. **Concerning**: Diffusion loss regressed +0.76 at step 40k, S1 accuracy dropped -7.5pp. AUROC stable ~0.86.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.21** | ✅ **MET** |
| AUROC > 0.75 | **0.857** | ✅ **MET** |
| ECE < 0.05 | **0.0072** | ✅ **MET** |
| Diff loss → 4.0 | **4.56** | ❌ **14% above** |
| S1 accuracy → 40% | **23.2%** | ❌ **42% below** |

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current v2**: AR performance on track to match v1. S1 training volatile - needs stabilization.

## Infrastructure
**13 sessions**, **$25.78 total cost** | Current: 14.9h uptime, no interruptions | Historical: frequent spot reclaims (sessions 2-12) causing training instability | **$19.37 saved** vs on-demand

## What's Next
**Critical**: Investigate diffusion loss regression and S1 accuracy volatility. After 50k: comprehensive v2 benchmarks, confidence calibration analysis, v1 vs v2 head-to-head comparison.