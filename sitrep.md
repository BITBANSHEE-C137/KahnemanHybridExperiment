# v3 Training Status SITREP

## v3 Training Status
**Step 44,000/50,000 (88%)** | GPU: 100% util, 82°C, L4 | Rate: ~200 steps/hr | **ETA: 30hrs** | Spot: $0.43/hr (-57% vs on-demand) | Current session: 7.1hr uptime

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 37k  | 28.51  | 4.52      | 24.1%  | 0.856 | 0.006 |
| 38k  | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 39k  | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40k  | 28.27  | 3.76      | 30.3%  | **0.881** | 0.009 |
| 41k  | 28.30  | 3.95      | 27.8%  | 0.866 | 0.011 |
| 42k  | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43k  | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| **44k** | **28.07** | **4.40** | **24.9%** | **0.867** | **0.010** |

**Trends**: AR PPL **improving steadily** (-1.6% over 7k steps). Diff loss **volatile**, recent uptick concerning. S1 accuracy **stalled** around 25-30%, down from 40k peak. AUROC stable ~0.87. ECE well-controlled <0.015.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.07** | ✅ **BEAT** |
| AUROC > 0.75 | **0.867** | ✅ **BEAT** |
| ECE < 0.05 | **0.010** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.40** | ❌ **+10% over target** |
| S1 accuracy → 40% | **24.9%** | ❌ **38% below target** |

**3/5 targets met**. Diffusion loss regressed +17% from step 40k minimum. S1 accuracy concerning—peaked at 30% but trending down.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. 

**Current AR performance superior to v1** (28.07 vs 43.86 PPL). Diffusion component underperforming vs v1's S1 equivalent.

## Infrastructure
**21 spot sessions**, total cost **$35.36**. Major reclaims on 3/9 (10+ instances in 4hrs). Current session stable 7.1hr on g6.2xlarge. **57% savings** vs on-demand ($17 saved). No recent interruptions.

## What's Next
Target completion **~48hrs**. Post-v3: comprehensive benchmarks vs v1/v2, confidence calibration deep-dive, **investigate S1 accuracy plateau**—may need architectural tweaks for v4.