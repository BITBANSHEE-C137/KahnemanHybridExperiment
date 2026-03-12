# v3 Training SITREP

## v3 Training Status
**Training complete** - Step **50,000/50,000** (100%)  
Current instance idle (0% GPU util, trainer stopped)  
Current spot: g5.2xlarge @ $0.48/hr (60.7% savings)  
Uptime: 9.3hrs, cost: $4.45

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | 4.40 | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | 3.94 | 28.1% | 0.866 | 0.016 |
| 47000 | 28.09 | 3.88 | 29.3% | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | 4.41 | 24.9% | 0.867 | 0.012 |
| **50000** | **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR PPL stable ~28 (good). Diff loss volatile 3.9-4.4. S1 accuracy peaked at 29.3% then regressed. AUROC stable ~0.87. ECE acceptable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **27.99** | ✅ **Met** |
| AUROC | > 0.75 | **0.870** | ✅ **Met** |
| ECE | < 0.05 | **0.012** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.16** | 🟡 **Close** |
| S1 Accuracy | → 40% | **26.5%** | ❌ **Gap: -13.5%** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**v3 AR better than v1** (27.99 vs 43.86 WikiText est.), **S1 similar** (4.16 vs 4.12)

## Infrastructure
**23 sessions, $40.35 total cost**  
Spot reclaim chaos Mar 9: 12 interruptions in 6hrs (steps 19.3k-20.4k)  
Stable since Mar 10: only 3 reclaims over 40+ hours  
Average savings: ~55% vs on-demand  
Current instance stable 9.3hrs

## What's Next
**v3 complete** - trigger benchmark suite (LAMBADA, WikiText-103)  
Compare v1 vs v3: expect **significant AR improvement**, similar S1 performance  
Analyze confidence head calibration on longer sequences  
Start v4 planning with improved S1 training recipe