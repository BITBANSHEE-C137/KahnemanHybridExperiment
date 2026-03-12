# v3 Training SITREP

## v3 Training Status
**TRAINING COMPLETE** - Step **50,000/50,000** (100%). GPU idle on g6.2xlarge (L4). Final checkpoint synced at 01:08 UTC. No active training - **awaiting v3 restart or benchmark phase**.

Current spot: $0.42/hr (57% savings), uptime 17min. ETA: Complete.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 28.14  | 4.196     | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.404     | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.159     | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.943     | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.883     | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.192     | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | 4.407     | 24.9%  | 0.867 | 0.012 |
| **50000** | **27.99** | **4.163** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR PPL stable ~28, modest improvement. Diff loss volatile 3.88-4.41. S1 accuracy peaked at 29.3% (step 47k), regressed. AUROC/ECE stable and strong.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.163** | ❌ **4% above** |
| S1 accuracy → 40% | **26.5%** | ❌ **34% below** |

**3/5 targets met**. Diffusion and S1 accuracy lagging.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12.
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL.

v3 vs v1: **AR improved** (28.0 vs 43.9 PPL), **S1 regressed** (4.16 vs 4.12 loss).

## Infrastructure
**25 sessions**, $40.48 total cost. Recent instability - **4 spot reclaims** in 10 hours (Mar 9 17:00-21:00). Switched g5→g6 instances for stability. Last 24hrs: 2 brief reclaims, training completed successfully.

Current: g6.2xlarge us-east-1b, 17min uptime, no issues.

## What's Next
**v3 training complete**. Priority queue:
1. **Run v3 benchmarks** (LAMBADA, WikiText-103)
2. **v1 vs v3 comparison analysis** 
3. **Confidence head deep-dive** - investigate AUROC plateau
4. Consider **v4 hyperparameter sweep** for S1/diffusion targets

Ready for benchmark phase.