# SITREP: v2 Training Status

*2026-03-05 06:30 UTC*

## v2 Training Status
**Step 14,700/50,000 (29.4%)** | GPU: **98.0%** util, 200W/300W, 52°C | Rate: ~4.8 steps/min | **ETA: 5.1 days** | Spot: **$0.44/hr** (63.9% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | Conf AUROC | ECE |
|------|--------|-----------|--------|------------|-----|
| 7000 | 27.12 | 5.13 | 17.9% | 0.833 | 0.0081 |
| 8000 | 27.58 | 4.65 | 21.1% | 0.845 | 0.0071 |
| 9000 | 28.06 | 5.02 | 18.9% | 0.843 | 0.0057 |
| 10000 | 28.39 | 4.37 | 25.1% | 0.850 | 0.0044 |
| 11000 | 28.91 | 4.19 | 26.0% | 0.857 | 0.0046 |
| 12000 | 29.35 | 4.34 | 25.6% | 0.852 | 0.0093 |
| 13000 | 30.50 | 4.40 | 25.5% | 0.852 | 0.0124 |
| 14000 | 30.34 | 4.31 | 26.0% | 0.853 | 0.0111 |

**⚠️ AR PPL trending upward** - degraded 12% since step 7k. **🔥 Confidence calibration deteriorating** - ECE doubled since step 11k. S1 accuracy plateaued around 25%.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.34** | ✅ |
| AUROC > 0.75 | **0.853** | ✅ |
| ECE < 0.05 | **0.0111** | ✅ |
| Diff loss → 4.0 | **4.31** | ⚠️ (close) |
| S1 accuracy → 40% | **26.0%** | ❌ |

**3/5 targets met**. Diffusion loss needs 0.31 drop, S1 accuracy needs 14pp gain.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current AR performance worse than v1** (30.34 vs ~27 expected from v1 metrics)

## Infrastructure
**10 spot reclaims** in 1.3 days - **high churn**. Total cost: **$10.49** vs $53.12 on-demand. Current session: 1.3hrs uptime, stable in us-east-1f. Checkpointing every 1k steps, last at 14k.

## What's Next
Monitor AR PPL regression - may need LR adjustment. Target completion in **5 days** if stable. Then: v2 benchmarks on LAMBADA/WikiText, confidence head analysis, v1 vs v2 head-to-head comparison.