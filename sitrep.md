# v3 Training SITREP

## v3 Training Status
**Step 21,700/50,000** (43.4% complete) | GPU: **100% util** A10G @ 54°C | Rate: ~2.9 steps/min | **ETA: 12.4 days** | Spot cost: **$0.48/hr** (60.7% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 14000 | 28.51  | 4.29      | 24.7%   | 0.852 | 0.0087 |
| 15000 | 28.64  | 4.50      | 23.7%   | 0.864 | 0.0052 |
| 16000 | 28.66  | 4.38      | 23.5%   | 0.856 | 0.0104 |
| 17000 | 28.89  | 4.34      | 25.2%   | 0.858 | 0.0079 |
| 18000 | 28.99  | 4.44      | 23.0%   | 0.858 | 0.0098 |
| 19000 | 29.21  | 4.39      | 22.1%   | 0.866 | 0.0106 |
| 20000 | 29.22  | 4.24      | 26.8%   | 0.857 | 0.0048 |
| 21000 | **29.94** | 4.26   | 26.8%   | 0.856 | 0.0116 |

**Concerning trend**: AR perplexity degrading (+1.4 since step 14k). S1 accuracy volatile but recent recovery to 26.8%. AUROC stable ~0.85-0.86. ECE acceptable but variable.

## Target Scorecard
- ❌ **AR PPL < 40**: 29.94 (PASS - but trending wrong direction)  
- ✅ **AUROC > 0.75**: 0.856 (PASS)
- ✅ **ECE < 0.05**: 0.0116 (PASS)
- ❌ **Diff loss → 4.0**: 4.26 (6.5% above target)
- ❌ **S1 accuracy → 40%**: 26.8% (33% below target)

**3/5 targets met**. Primary concerns: S1 accuracy plateau and AR perplexity drift.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance (29.94) comparable to v1 baseline but concerning upward trend**.

## Infrastructure
**18 spot reclaims** since training start - excessive instability. Current session: 2.2hrs uptime on g5.2xlarge. Total cost: **$18.17** across mixed instance types. Frequent interruptions impacting training efficiency but aggressive spot usage maintaining 60%+ savings.

## What's Next
**Immediate**: Monitor AR perplexity trend - may need LR adjustment if degradation continues. Investigate S1 accuracy plateau around 27%. Consider checkpoint rollback if metrics don't stabilize by step 25k.