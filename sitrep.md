# v2 Training SITREP

## v2 Training Status
**Step 24,800/50,000** (49.6% complete) | A10G **100% GPU util** @ 200W/300W | **1.16 hr uptime** | Rate: ~7.1 steps/min | **ETA: 59 hrs** | Current spot: **$0.45/hr** (63% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|--------|------------|----------|
| 17000 | 30.70  | 4.52      | 23.7%  | 0.860      | 0.0074   |
| 18000 | 30.77  | 4.03      | 27.2%  | 0.869      | 0.0060   |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860      | 0.0073   |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851      | 0.0072   |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851      | 0.0075   |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858      | 0.0096   |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864      | 0.0095   |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863      | 0.0050   |

**Trends:** AR perplexity **stable ~31** (slight uptick). Diffusion loss **volatile 4.0-4.9 range**. S1 accuracy **stuck 20-28%**. AUROC solid **>0.85**. ECE improving **<0.01**.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.98** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.005** | ✅ **MET** |
| Diff loss → 4.0 | **4.46** | ❌ **Above target** |
| S1 accuracy → 40% | **24.3%** | ❌ **Below target** |

**3/5 targets met**. Diffusion loss needs **10% improvement**. S1 accuracy needs **65% boost**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. **Current v2 AR PPL (30.98) significantly better than v1 (43.86)**. S1 performance regressing vs v1's 67% loss drop achievement.

## Infrastructure
**12 spot sessions**, **$16.98 total cost** vs $38.22 on-demand (56% savings). Current session stable **1.2hrs** in us-east-1a. **No recent spot reclaims** - longest session was 10hrs. Instance type switching (g5.xlarge/2xlarge) for cost optimization.

## What's Next
Training **25 hours remaining** at current rate. Focus on S1 accuracy plateau and diffusion loss convergence. Post-completion: comprehensive v1/v2 benchmarks, confidence calibration deep-dive, joint training impact analysis.