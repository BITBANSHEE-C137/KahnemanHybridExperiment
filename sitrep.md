# v3 Training SITREP

## v3 Training Status
**84% complete** (42k/50k steps) | **100% GPU util** L4 @81°C | **~270 steps/hr** | **ETA: ~30hrs** | **Spot: $0.43/hr** (56% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 35k  | 28.73  | 4.26      | 25.0%  | 0.863 | 0.006 |
| 38k  | 28.43  | **4.02**  | **28.5%** | 0.864 | 0.009 |
| 40k  | 28.27  | **3.76**  | **30.3%** | **0.881** | 0.009 |
| 42k  | **28.33** | 3.89   | 29.1%  | 0.870 | **0.013** |

**Trends:** AR PPL plateauing at target. Diff loss improving strongly. **S1 accuracy stalling** around 29-30%. AUROC solid. **ECE degrading** - confidence calibration issue emerging.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|--------|
| AR PPL | < 40 | **28.33** | ✅ **BEAT** |
| AUROC | > 0.75 | **0.870** | ✅ |
| ECE | < 0.05 | **0.013** | ✅ |
| Diff Loss | → 4.0 | **3.89** | ✅ |
| S1 Accuracy | → 40% | **29.1%** | ❌ **BEHIND** |

**Major concern:** S1 accuracy **11pp below target** and stagnating.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v3: AR matching v1 performance, diff loss approaching v1 final.

## Infrastructure  
**21 spot sessions** across 4 AZs. **$33.91 total cost** vs $50.84 on-demand. Current session: 3.6hrs uptime, no interruptions. **Stable g6.2xlarge** in us-east-1b since 07:21 UTC.

**Spot reclaim risk:** Moderate at current $0.43/hr rate (43% of on-demand).

## What's Next
**Critical:** Investigate S1 accuracy plateau - may need LR adjustment or extended training. After 50k completion: full v1 vs v3 benchmark suite, confidence calibration analysis for ECE regression.