# v2 Training SITREP - March 5, 2026

## v2 Training Status
**Step 17,600/50,000 (35.2%)** | GPU: **100%** util, 202W/300W, 52°C | Rate: ~400 steps/hr | **ETA: ~3.4 days** | Current spot: **$0.44/hr** (64% savings) | Session cost: **$2.09**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 10k  | 28.39  | 4.37      | 25.1%   | 0.850 | 0.004 |
| 11k  | 28.91  | 4.19      | 26.0%   | 0.857 | 0.005 |
| 12k  | 29.35  | 4.34      | 25.6%   | 0.852 | 0.009 |
| 13k  | 30.50  | 4.40      | 25.5%   | 0.852 | 0.012 |
| 14k  | 30.34  | 4.31      | 26.0%   | 0.853 | 0.011 |
| 15k  | 31.05  | 4.33      | 26.1%   | 0.852 | 0.014 |
| 16k  | 30.79  | 4.13      | 26.8%   | 0.860 | 0.007 |
| 17k  | **30.70** | **4.52** | **23.7%** | **0.860** | **0.007** |

**Trends**: AR PPL plateaued ~30-31 (concerning). S1 accuracy **regressed 3%** at 17k. AUROC improved to 0.860. ECE unstable but acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **30.7** | ✅ **MET** |
| AUROC > 0.75 | **0.860** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **4.52** | ❌ **13% above** |
| S1 accuracy → 40% | **23.7%** | ❌ **41% below** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.7) matches v1 final but still 6% worse than GPT-2**.

## Infrastructure
**10 spot sessions** | Total cost: **$12.02** | Current uptime: 4.8hrs | **Multiple reclaims** in us-east-1b (sessions 2-5). Stable in us-east-1f since 5:13 UTC. Instance type varied (g5.xlarge attempts failed).

## What's Next
**Red flags**: S1 accuracy regression and diff loss stagnation. Consider learning rate adjustment. After v2 completes: comprehensive benchmarks, detailed v1 vs v2 analysis, investigate confidence head calibration improvements.