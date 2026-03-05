# v2 Training SITREP - Step 22,100

## v2 Training Status
**44.2% complete** (22,100/50k steps) | **100% GPU util** A10G @ 197W/300W, 54°C | **ETA ~13.5 hours** at current pace | Current spot: **$0.45/hr** (62.9% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 15000 | 31.05  | 4.33      | 26.1%  | 0.852 | 0.014 |
| 16000 | 30.79  | 4.13      | 26.8%  | 0.860 | 0.007 |
| 17000 | 30.70  | 4.52      | 23.7%  | 0.860 | 0.007 |
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000 | **30.95** | **4.19** | **27.5%** | **0.858** | **0.010** |

**Trends**: AR PPL stable ~31. **⚠️ S1 accuracy volatile** (20.7% → 27.5% jump). Diffusion loss noisy. AUROC plateau around 0.86.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **30.95** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.0096** | ✅ **MET** |
| Diff loss → 4.0 | **4.19** | 🟡 Close |
| S1 accuracy → 40% | **27.5%** | ❌ **Need +12.5%** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (30.95) significantly better than v1 WikiText (43.86)**.

## Infrastructure
**11 spot sessions** over 2.3 days | Total cost **$15.35** vs $43.73 on-demand | **10 spot reclaims** but consistent recovery | Current session: 2.3hrs uptime, us-east-1b stable

## What's Next
**~28k steps remaining**. S1 accuracy needs significant improvement - consider learning rate schedule adjustment. After completion: comprehensive v1 vs v2 benchmarking, confidence calibration deep dive.