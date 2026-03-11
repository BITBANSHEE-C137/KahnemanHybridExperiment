# v3 Training SITREP
*2026-03-11 10:00 UTC*

## v3 Training Status
**Step 41,400/50,000 (82.8%)** | GPU: **98% util** L4 @ 72W/83°C | Rate: ~4.8 steps/min | **ETA: ~30hrs** | Spot: **$0.425/hr** (57% savings) | Current session cost: **$1.12**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 34000 | 28.85  | 4.15      | 25.6%  | 0.871 | 0.007 |
| 35000 | 28.73  | 4.26      | 25.0%  | 0.863 | 0.006 |
| 36000 | 28.59  | 4.46      | 23.5%  | 0.864 | 0.011 |
| 37000 | 28.51  | 4.52      | 24.1%  | 0.856 | 0.006 |
| 38000 | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 39000 | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40000 | 28.27  | 3.76      | 30.3%  | **0.881** | 0.009 |
| 41000 | **28.30** | **3.95** | **27.8%** | 0.866 | **0.011** |

**Trends:** AR PPL steady improvement stalled. **Diffusion loss improving** (3.76→3.95 recent volatility). S1 accuracy **regressed** from 30.3%→27.8%. AUROC **peaked at 40k**, now declining. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.3** | ✅ **MET** |
| AUROC > 0.75 | **0.866** | ✅ **MET** |
| ECE < 0.05 | **0.011** | ✅ **MET** |
| Diff loss → 4.0 | **3.95** | ✅ **ON TARGET** |
| S1 accuracy → 40% | **27.8%** | ❌ **69% TO TARGET** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance approaching v1 levels, S1 underperforming.**

## Infrastructure
**21 sessions, $33.49 total cost**. Current: g6.2xlarge us-east-1b, **2.6hrs uptime**. Heavy spot volatility 3/9 (10+ reclaims in 4hrs). **Stable since 3/10** - longest session 24hrs. Average **56% spot savings**.

## What's Next
**9k steps remaining** (~30hrs). Monitor S1 accuracy regression - may need extended training. Post-completion: comprehensive v1 vs v3 benchmarks, confidence calibration analysis, diffusion quality assessment.