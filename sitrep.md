# v3 Training Status SITREP

## v3 Training Status
**COMPLETE** - **50,000/50,000 steps (100%)**. Current instance idle (step 0 reset for new run). A10G GPU at 0% util, 21°C. Training completed at step 50k on 2026-03-12 01:08 UTC. Spot rate: **$0.48/hr** (60.7% savings). No active training.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 28.14  | 4.196     | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | **4.404** | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.159     | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | **3.943** | 28.1%  | 0.866 | **0.016** |
| 47000 | 28.09  | **3.883** | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.192     | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | **4.407** | 24.9%  | 0.867 | 0.012 |
| 50000 | **27.99** | 4.163  | 26.5%  | **0.870** | 0.012 |

**Trends**: AR PPL stable ~28, slight improvement final step. Diffusion loss volatile (3.88-4.41). S1 accuracy plateaued mid-20s%. AUROC consistent ~0.87. ECE well-controlled <0.016.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | ❌ **MISS** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. Diffusion loss stuck above target. S1 accuracy significantly below 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. 
Current v3: **AR PPL improved 36% vs WikiText baseline** (28 vs 44). S1 performance similar to v1 baseline. **Need v3 benchmark runs for proper comparison**.

## Infrastructure
**Total cost: $40.35** across 23 sessions. Major instability 3/9-3/10 with **12 spot reclaims** in ~24hrs. Stabilized on g6.2xlarge instances for final 10k steps. Current session: 8.3hrs uptime, $4.0 spent. **Spot market highly volatile** - frequent instance type switching required.

## What's Next
1. **Run v3 benchmarks** on completed 50k model
2. v1 vs v3 detailed comparison (expect AR improvement, S1 plateau)
3. Analyze confidence head calibration vs diffusion performance
4. **Address S1 accuracy regression** - may need architecture/training changes

**Bottom line**: v3 training complete with good AR performance but **S1 accuracy plateau is concerning**. Infrastructure costs reasonable despite spot volatility.