## v3 Training Status
**Step 44,600/50,000 (89.2%)** - **ETA: ~3.5 hrs**. L4 GPU at **100% util**, 69W/72W, 78°C. Training rate ~1.57 steps/sec. Current spot: **$0.43/hr** (56% savings vs on-demand). **8.1 hrs uptime** on current instance.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 37k   | 28.51  | 4.52      | 24.1%  | 0.856 | 0.006 |
| 38k   | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 39k   | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40k   | 28.27  | 3.76      | 30.3%  | 0.881 | 0.009 |
| 41k   | 28.30  | 3.95      | 27.8%  | 0.866 | 0.011 |
| 42k   | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43k   | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| **44k** | **28.07** | **4.40** | **24.9%** | **0.867** | **0.010** |

**Trends**: AR PPL steady decline (good). Diff loss **volatile** around 4.0 target. S1 accuracy **regressing** from 30% peak. AUROC stable ~0.87. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.07** | ✅ **MET** |
| AUROC > 0.75 | **0.867** | ✅ **MET** |  
| ECE < 0.05 | **0.010** | ✅ **MET** |
| Diff loss → 4.0 | **4.40** | ❌ **10% over** |
| S1 accuracy → 40% | **24.9%** | ❌ **38% short** |

**3/5 targets met**. S1 accuracy concerning - **peaked at 30% then declined**. Diff loss needs stabilization.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR PPL (28.07) beating v1 (43.86) by 36%** and approaching GPT-2 baseline.

## Infrastructure
**21 spot sessions**, **$35.79 total cost**. Current g6.2xlarge stable 8h. Previous: 10 spot reclaims 3/9, mostly brief interruptions. **Cost efficiency excellent** - projected $7.39 vs $17 on-demand.

## What's Next  
**5.4k steps remaining** (~3.5 hrs). Focus: **stabilize diff loss**, investigate S1 accuracy regression. Post-completion: v3 benchmarks vs v1/GPT-2, confidence calibration analysis, cost/performance comparison.