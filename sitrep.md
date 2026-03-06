# v2 Training SITREP

## v2 Training Status
**Step 42,300/50,000 (84.6%)** • A10G @ **99% util** • **7.4 steps/min** • ETA: **17h** • Spot: **$0.46/hr** (62% savings)

Current session: 1.8h uptime, **$0.79** cost

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 35000 | 30.84  | 4.79      | 21.4%  | 0.855 | 0.011 |
| 36000 | 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 37000 | 30.65  | 4.75      | 21.6%  | 0.861 | 0.007 |
| 38000 | 30.44  | 4.28      | 26.7%  | 0.865 | 0.004 |
| 39000 | 30.41  | 3.80      | 30.7%  | 0.863 | 0.007 |
| 40000 | 30.21  | 4.56      | 23.2%  | 0.857 | 0.007 |
| 41000 | 30.12  | 4.47      | 25.1%  | 0.862 | 0.012 |
| 42000 | **30.08** | **4.07** | **29.0%** | **0.862** | **0.016** |

**Trends**: AR PPL improving steadily. Diff loss volatile but trending down. S1 accuracy recovering from step 40k dip. **ECE degrading** - confidence calibration concern.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **30.08** | ✅ |
| AUROC > 0.75 | **0.862** | ✅ |
| ECE < 0.05 | **0.016** | ✅ |
| Diff loss → 4.0 | **4.07** | ✅ |
| S1 accuracy → 40% | **29.0%** | ❌ |

**4/5 targets met**. S1 accuracy needs **+11pp** improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

v2 AR performance **better than v1** (30.08 vs 43.86 PPL). Diff loss approaching v1 S1 target.

## Infrastructure
**15 spot sessions**, **$27.12** total cost across 2.5 days
Recent stability: Current session 1.8h, prev session 16h (longest yet)
**No recent interruptions** - spot market stable in us-east-1b

## What's Next
7.7k steps remaining (**17h ETA**). Post-completion: v2 benchmarks, direct v1/v2 comparison, confidence calibration analysis (ECE trend concerning). S1 accuracy trajectory suggests **may miss 40% target**.