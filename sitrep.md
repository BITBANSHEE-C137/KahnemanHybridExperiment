## v2 Training Status
**Step 26,100/50,000 (52.2%)** | A10G at **99% util**, 199W/300W, 48°C | Rate: ~2.8 steps/min | **ETA: ~14.2 days** | Spot cost: **$0.45/hr** (63% savings) | Current session uptime: 2.8hrs

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 19k  | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20k  | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21k  | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22k  | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23k  | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24k  | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25k  | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012 |
| 26k  | **31.46** | 4.06   | **28.0%** | 0.863 | **0.018** |

**Concerning trends**: AR PPL slowly degrading (+0.65 since 19k), ECE spiking to 0.018. Diffusion loss volatile but improving. S1 accuracy recovering after 20-21k dip.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **31.46** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.018** | ✅ **MET** |
| Diff loss → 4.0 | **4.06** | ✅ **NEAR** |
| S1 accuracy → 40% | **28.0%** | ❌ **BEHIND** |

**3/5 targets met**. S1 accuracy lagging significantly (12pp gap). ECE trending wrong direction.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

Current v2 AR PPL (**31.46**) better than v1 WikiText baseline, suggesting **improved AR performance**.

## Infrastructure
**12 spot reclaims** in 2.5 days - extremely unstable. Total cost **$17.69** vs $38.44 on-demand. Current g5.2xlarge session stable for 2.8hrs in us-east-1a. Cost trajectory: **$14.38 projected** (vs $24.31 baseline).

**High spot volatility impacting training continuity**.

## What's Next
**Critical**: Address ECE degradation and S1 accuracy plateau. After completion (~19 days): comprehensive v1 vs v2 benchmarks, confidence calibration analysis, cost-performance comparison. May need spot diversification strategy.