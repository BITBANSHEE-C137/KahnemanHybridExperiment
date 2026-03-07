# v2 Training SITREP

## v2 Training Status
**Step 48,100/50,000 (96.2%)** - **1,900 steps remaining**  
A10G @ 100% util, 200W/300W, 50°C, 16.6GB/23GB VRAM  
Rate: ~1.3 steps/min | **ETA: ~24 hours**  
Spot: $0.46/hr (61.8% savings) | Current session cost: **$4.07**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 41000| 30.12   | 4.47      | 25.1%   | 0.862 | 0.012 |
| 43000| 29.96   | 3.93      | 29.2%   | 0.868 | 0.020 |
| 45000| 29.80   | 3.86      | 29.3%   | **0.875** | 0.016 |
| 47000| 29.72   | 4.61      | 22.7%   | 0.855 | 0.011 |
| 48000| **29.72** | **4.73** | **21.9%** | 0.858 | **0.012** |

**Trends**: AR PPL plateaued at ~29.7. **Diff loss regressing** (3.86→4.73). **S1 accuracy declining** (29.3%→21.9%). AUROC dropped from peak 0.875. ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.72** | ✅ |
| AUROC | > 0.75 | **0.858** | ✅ |
| ECE | < 0.05 | **0.012** | ✅ |
| Diff Loss | → 4.0 | **4.73** | ❌ |
| S1 Accuracy | → 40% | **21.9%** | ❌ |

**3/5 targets met**. Diffusion and S1 underperforming significantly.

## v1 Benchmark Baseline  
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
Current v2 AR PPL (**29.72**) matches GPT-2 baseline - **no regression from joint training**.

## Infrastructure
**15 spot sessions**, $30.37 total cost (current session: 8.8h uptime)  
Multiple reclaims (longest: 15.9h session), mostly stable on g5.2xlarge  
Current instance stable since 17:42 UTC yesterday

## What's Next
Training completes in ~24h. **Priority**: Investigate diffusion loss regression and S1 accuracy decline. Run full v2 benchmarks, compare confidence calibration vs v1. Diffusion component may need architectural review.