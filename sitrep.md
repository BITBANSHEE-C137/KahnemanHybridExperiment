# v3 Training SITREP

## v3 Training Status
**Step 48,400/50,000 (96.8%)** - ETA: ~1h 30m at current rate  
GPU: **100% util**, L4 running hot at 80°C, 72W VRAM: 16.6/23GB  
Spot rate: **$0.463/hr** (53% savings vs on-demand $0.98/hr)  
Current session cost: **$2.76**, projected total: **$4.01**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 41000 | 28.30  | 3.949     | 27.8%  | 0.866 | 0.011 |
| 42000 | 28.33  | 3.892     | 29.1%  | 0.870 | 0.013 |
| 43000 | 28.14  | 4.196     | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.404     | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.159     | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.943     | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.883     | 29.3%  | 0.870 | 0.014 |
| **48000** | **28.04** | **4.192** | **26.1%** | **0.870** | **0.012** |

**Trends:** AR PPL plateaued ~28. Diffusion loss volatile (3.9-4.4). S1 accuracy stagnant 25-29%. AUROC stable 0.87. ECE well controlled.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.04** | ✅ **PASS** |
| AUROC | > 0.75 | **0.870** | ✅ **PASS** |
| ECE | < 0.05 | **0.012** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.192** | ❌ Close |
| S1 Accuracy | → 40% | **26.1%** | ❌ **Underperforming** |

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR performance better than v1** (28.04 vs 43.86 PPL). S1 token accuracy concerning - v1 achieved much lower loss.

## Infrastructure
**22 spot sessions**, total cost **$39.00** across 3 days  
Current session: 6h uptime, g6.2xlarge us-east-1a, stable  
**Spot interruption history:** Severe instability 3/9 (11 reclaims in 4h), stabilized on g6.2xlarge instances since 3/10

## What's Next
**1,600 steps to completion** - monitoring S1 accuracy plateau. Post-v3: comprehensive benchmark suite vs v1/v2, confidence calibration analysis, investigate S1 underperformance root cause.