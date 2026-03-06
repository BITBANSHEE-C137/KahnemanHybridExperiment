# ML Ops SITREP - v2 Training

## v2 Training Status
**Step 40,600/50,000** (**81.2%** complete) | A10G @ **100%** util, 195W/300W | **15.4 hrs remaining** at current rate | Spot: **$0.46/hr** (**62.6% savings**) | Current session cost: **$6.96**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 33000 | 31.29  | 4.23      | 0.254  | 0.864 | 0.0075 |
| 34000 | 31.13  | 4.68      | 0.220  | 0.854 | 0.0086 |
| 35000 | 30.84  | 4.79      | 0.214  | 0.855 | 0.0109 |
| 36000 | 30.69  | 4.30      | 0.248  | 0.863 | 0.0100 |
| 37000 | 30.65  | 4.75      | 0.216  | 0.861 | 0.0069 |
| 38000 | 30.44  | 4.28      | 0.267  | 0.865 | 0.0042 |
| 39000 | 30.41  | 3.80      | 0.307  | 0.863 | 0.0068 |
| **40000** | **30.21** | **4.56** | **0.232** | **0.857** | **0.0072** |

**Trends**: AR PPL steadily improving ✓ | Diff loss volatile but trending down ✓ | S1 accuracy highly volatile, **regressed at 40k** ⚠️ | AUROC stable ~0.86 ✓ | ECE excellent <0.01 ✓

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.21** | ✅ **Met** |
| AUROC > 0.75 | **0.857** | ✅ **Met** |
| ECE < 0.05 | **0.007** | ✅ **Met** |
| Diff loss → 4.0 | **4.56** | 🔄 **14% above** |
| S1 accuracy → 40% | **23.2%** | ❌ **42% below** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
v2 AR performance **31% better** than v1 WikiText. S1 token accuracy **concerning volatility**.

## Infrastructure
**13 spot sessions**, **$26 total cost** vs $32.52 on-demand. **Current session stable 15.4hrs**, no recent interruptions. Previous sessions averaged 4.3hrs before reclaim. Cost tracking accurate across AZ migrations (1a/1b/1f).

## What's Next
**9,400 steps remaining** (~15hrs). Post-completion: comprehensive v1/v2 benchmarking, **investigate S1 accuracy regression pattern**, confidence calibration deep-dive. S1 volatility suggests potential training instability requiring analysis.