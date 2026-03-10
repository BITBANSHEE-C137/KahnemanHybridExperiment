## v3 Training Status
**Step 21,200/50,000 (42.4%)** running on g5.2xlarge spot @ **$0.48/hr** (60.7% savings). GPU at **100% util**, 202W/300W, 56°C. **1.69 hrs uptime**, current session stable. ETA: ~34 hours at current rate.

## Eval Metrics & Trends

| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 14000 | 28.51 | 0.852 | 0.009 | 4.29 | 24.7% |
| 16000 | 28.66 | 0.856 | 0.010 | 4.38 | 23.5% |
| 18000 | 28.99 | 0.858 | 0.010 | 4.44 | 23.0% |
| 20000 | **29.22** | 0.857 | **0.005** | **4.24** | **26.8%** |
| 21000 | **29.94** | 0.856 | 0.012 | 4.26 | 26.8% |

**Trends:** AR perplexity **degrading** (+1.4 since step 14k). AUROC stable ~0.856. ECE volatile but acceptable. Diff loss improving toward target. S1 accuracy recovered to ~27% after dip.

## Target Scorecard
- **AR PPL < 40:** ✅ **29.94** (healthy margin)
- **AUROC > 0.75:** ✅ **0.856** (solid)
- **ECE < 0.05:** ✅ **0.012** (excellent calibration)
- **Diff loss → 4.0:** 🟡 **4.26** (trending right direction)
- **S1 accuracy → 40%:** ❌ **26.8%** (need +13.2pp)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR PPL (29.94) significantly better than v1 WikiText (43.86)** and approaching GPT-2 baseline. S1 accuracy still lagging target.

## Infrastructure
**18 spot interruptions** causing training instability. Multiple failed g6.xlarge attempts (steps stuck at 20.1k-20.5k range). Current g5.2xlarge session **stable for 1.7hrs**. Total cost: **$17.93** vs $44.33 on-demand (**60.7% savings**).

## What's Next
**Critical:** Address spot interruption cascade - consider reserved capacity or multi-AZ strategy. Monitor AR PPL trend (degrading). Target S1 accuracy boost needed. After v2 completes: comprehensive v1/v2 benchmark comparison, confidence calibration deep-dive.