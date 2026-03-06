# v2 Training Status SITREP

## v2 Training Status
**Step 36,900/50,000 (73.8%)** | A10G @ 100% util, 189W/300W | **11.0 hrs ETA** | Spot: $0.45/hr (**62.7% savings**) | Rate: ~1k steps/hr

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 29000 | 31.43  | 4.21      | 27.7%   | 0.860 | 0.022 |
| 30000 | 31.68  | 4.08      | 28.1%   | 0.864 | 0.023 |
| 31000 | 31.60  | 4.49      | 24.5%   | 0.862 | 0.014 |
| 32000 | 31.39  | 3.96      | 28.4%   | **0.871** | 0.013 |
| 33000 | 31.29  | 4.23      | 25.4%   | 0.864 | 0.008 |
| 34000 | 31.13  | 4.68      | 22.0%   | 0.854 | 0.009 |
| 35000 | 30.84  | 4.79      | 21.4%   | 0.855 | 0.011 |
| **36000** | **30.69** | **4.30** | **24.8%** | **0.863** | **0.010** |

**Trends:** AR PPL steadily improving ✅ | Diff loss volatile, trending up ⚠️ | S1 accuracy plateaued ~25% | AUROC stable | ECE excellent <0.02

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.69** | ✅ **BEAT** |
| AUROC > 0.75 | **0.863** | ✅ **BEAT** |
| ECE < 0.05 | **0.010** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.30** | ❌ Stalled |
| S1 accuracy → 40% | **24.8%** | ❌ **Far behind** |

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**v2 at 74%:** AR already **30% better** than v1 final (30.7 vs 43.9 PPL)

## Infrastructure
**13 sessions, 12 spot reclaims** | Current uptime: 10.9hrs | Total cost: **$23.93** (proj. $12.13 to completion)  
Spot stability: **Poor** - avg 3.6hr sessions, frequent AZ switching required

## What's Next
ETA **March 6 23:30 UTC** | Post-completion: v2 benchmarks, confidence head analysis, **investigate S1 accuracy regression** from diffusion loss instability