# v3 Training SITREP

## v3 Training Status
**Step 44,900/50,000 (89.8%)** • GPU: **99.0%** util, 72.5W/72W • Rate: ~300 steps/hr • **ETA: ~17 hrs** • Spot: **$0.42/hr** (56.5% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 37000 | 28.51 | 4.52 | 24.1% | 0.856 | 0.006 |
| 38000 | 28.43 | **4.02** | **28.5%** | 0.864 | 0.009 |
| 40000 | 28.27 | **3.76** | **30.3%** | **0.881** | 0.009 |
| 42000 | 28.33 | 3.89 | 29.1% | 0.870 | 0.013 |
| 44000 | **28.07** | 4.40 | 24.9% | 0.867 | **0.010** |

**Trends**: AR PPL improving steadily. **Concerning**: Diff loss volatile (3.76→4.40), S1 accuracy regressing from 30.3%→24.9%. AUROC stable ~0.87.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.07** | ✅ **PASS** |
| AUROC > 0.75 | **0.867** | ✅ **PASS** |
| ECE < 0.05 | **0.010** | ✅ **PASS** |
| Diff loss → 4.0 | **4.40** | ❌ Regressing |
| S1 accuracy → 40% | **24.9%** | ❌ **Far behind** |

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance ahead of v1** (28.07 vs 43.86), but **S1 training struggling** vs target.

## Infrastructure
**21 sessions**, **$36.00 total cost**. Current: g6.2xlarge, 8.6hr uptime, stable. **History**: Multiple spot reclaims 3/9 (step 20k range), then stable 24hr+ runs. g6.2xlarge most reliable.

## What's Next
**5,100 steps remaining**. Key concerns: **S1 accuracy plateau** needs investigation, diff loss volatility. Post-completion: v2 benchmarks, confidence calibration analysis, S1 token prediction deep dive.