# v2 Training SITREP

## v2 Training Status
**78.8% complete** (39,400/50,000 steps). GPU at **100% utilization**, A10G running cool at 52°C. Current rate: ~350 steps/hr. **ETA: 30 hours**. Spot cost: **$0.45/hr** (62.7% savings vs on-demand). Total spend: **$25.28**.

## Eval Metrics & Trends

| Step  | AR PPL | AUROC | ECE    | Diff Loss | S1 Acc |
|-------|--------|-------|--------|-----------|--------|
| 32000 | 31.39  | 0.871 | 0.0129 | 3.958     | 28.4%  |
| 33000 | 31.29  | 0.864 | 0.0075 | 4.234     | 25.4%  |
| 34000 | 31.13  | 0.854 | 0.0086 | 4.678     | 22.0%  |
| 35000 | 30.84  | 0.855 | 0.0109 | 4.789     | 21.4%  |
| 36000 | 30.69  | 0.863 | 0.0100 | 4.300     | 24.8%  |
| 37000 | 30.65  | 0.861 | 0.0069 | 4.755     | 21.6%  |
| 38000 | 30.44  | 0.865 | 0.0042 | 4.275     | 26.7%  |
| 39000 | 30.41  | 0.863 | 0.0068 | 3.795     | 30.7%  |

**Positive trends**: AR PPL steadily improving (31.39→30.41), ECE excellent (<0.01), S1 accuracy recovering (30.7% vs 22% trough). **Concerning**: Diffusion loss volatile (3.80-4.79), AUROC plateaued ~0.86.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.41** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.0068** | ✅ **MET** |
| Diff loss → 4.0 | **3.80** | ✅ **MET** |
| S1 accuracy → 40% | **30.7%** | ⚠️ **BEHIND** |

**4/5 targets met**. S1 accuracy trending up but needs **9.3pp** improvement.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%/WikiText 29.07 PPL. v2 AR performance tracking ahead of v1 (30.41 vs 43.86 PPL equivalent).

## Infrastructure
**13 spot sessions**, 6 reclaims in 3 days. Current instance stable 14hrs. Cost efficiency: 62.7% savings. Recent reclaim pattern suggests market volatility in us-east-1.

## What's Next
**10.6k steps remaining** (~30hrs). Focus: S1 accuracy push to 40%. Post-completion: v2 benchmarks, head-to-head v1/v2 comparison, confidence calibration analysis on final checkpoints.