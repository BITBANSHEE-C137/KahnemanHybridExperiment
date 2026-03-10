# v3 Training SITREP

## v3 Training Status
**Step 35,100/50,000** (70.2% complete) | **100% GPU util** | L4 @ 81°C, 72W power | **0.46 $/hr** spot rate | ETA: ~6.5 days | Current session cost: **$8.75**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|---------|-----------|-------------|-------|-----|
| 28000 | 29.40 | 4.51 | 23.8% | 0.865 | 0.0068 |
| 29000 | 29.36 | 4.27 | 25.5% | 0.867 | 0.0118 |
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.0046 |
| 31000 | 28.95 | 4.47 | 23.3% | 0.871 | 0.0031 |
| 32000 | 29.04 | 4.35 | 24.2% | 0.865 | 0.0089 |
| 33000 | 28.93 | 4.09 | 26.6% | 0.861 | 0.0086 |
| 34000 | 28.85 | 4.15 | 25.6% | **0.871** | 0.0069 |
| 35000 | **28.73** | 4.26 | 25.0% | 0.863 | **0.0057** |

**Trends:** AR PPL steadily improving. S1 accuracy volatile but trending up. AUROC plateaued ~0.86-0.87. **ECE excellent** at 0.006.

## Target Scorecard
- ✅ **AR PPL < 40**: 28.73 (met, improving)
- ✅ **AUROC > 0.75**: 0.863 (met, stable)
- ✅ **ECE < 0.05**: 0.0057 (met, excellent)
- ❌ **Diff loss → 4.0**: 4.26 (close, 6.5% over target)
- ❌ **S1 accuracy → 40%**: 25.0% (37.5% gap remaining)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 AR performance superior to v1** (28.73 vs 43.86 WikiText PPL). S1 task learning slowly.

## Infrastructure
**Current session:** g6.2xlarge, 19h uptime, **53% savings** vs on-demand
**Spot history:** 19 total sessions, frequent early reclaims (9-19 Mar)
**Total project cost:** $28.75 | Session stability improved on g6.2xlarge

## What's Next
15k steps remaining (~6 days). **S1 accuracy needs 15% improvement** to hit target. Diff loss close to 4.0 target. Post-completion: v1/v2 benchmarks, confidence calibration analysis, architecture ablations.