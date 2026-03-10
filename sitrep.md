# v3 Training SITREP

## v3 Training Status
**Step 30,700/50,000 (61.4%)** | GPU: **98%** util, L4 @ 82°C | Rate: ~300 steps/hr | ETA: **65 hours** | Spot: **$0.46/hr** (53% savings)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|---------|
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.0059 |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.0055 |
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.0042 |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.0063 |
| 27000 | 29.55  | 4.32      | 24.6%  | 0.866 | 0.0109 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.0068 |
| 29000 | 29.36  | 4.27      | 25.5%  | 0.867 | 0.0118 |
| 30000 | **29.16** | 4.34   | 24.6%  | **0.868** | **0.0046** |

**AR PPL trending down** (29.57→29.16). **AUROC improving** steadily. ECE volatile but within range. **S1 accuracy stagnant** around 24-27%.

## Target Scorecard
- ✅ **AR PPL < 40**: 29.16 (BEAT by 27%)
- ✅ **AUROC > 0.75**: 0.868 (BEAT by 16%)  
- ✅ **ECE < 0.05**: 0.0046 (BEAT by 91%)
- ❌ **Diff loss → 4.0**: 4.34 (7% over target)
- ❌ **S1 accuracy → 40%**: 24.6% (38% under target)

**3/5 targets met**. Confidence head performing excellently. **S1 system underperforming**.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**v3 AR performance on track** (29.16 vs 43.86 target). S1 accuracy concerning vs baseline expectations.

## Infrastructure
**19 spot sessions** over 3 days. Current: g6.2xlarge stable **11.6hr uptime**. Total cost: **$25.29** (vs $43.34 on-demand).

Notable: Multiple brief reclaims 3/9 PM (steps 20k-20.5k), now stable on L4. Average **53% cost savings**.

## What's Next
Target step 35k eval for trend confirmation. **S1 system needs investigation** - accuracy plateau concerning. Post-50k: comprehensive v1 vs v3 benchmarks, confidence calibration analysis.