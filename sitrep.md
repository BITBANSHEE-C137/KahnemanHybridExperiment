# v3 Training SITREP

## v3 Training Status
**COMPLETE** - Training finished at **step 50,000/50,000** (100%). Current instance idle after completion. GPU: 0% utilization, NVIDIA A10G cold (29°C). Spot rate: **$0.47/hr** (60.8% savings vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|--------|-------|
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869  | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867  | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870  | 0.011 |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866  | 0.016 |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870  | 0.014 |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870  | 0.012 |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867  | 0.012 |
| 50000 | 27.99  | 4.16      | 26.5%  | 0.870  | 0.012 |

**Trends**: AR PPL stable ~28, no convergence. Diffusion loss oscillating 3.9-4.4 without clear trend. S1 accuracy volatile 25-29%. AUROC rock solid 0.87. ECE well-controlled <0.016.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | 🔶 **CLOSE** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. AR performing well, confidence calibration excellent. S1 accuracy plateau at ~26%, far from 40% target.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. 
v3 AR regressed: **27.99 vs 43.86 PPL** (36% improvement). S1 diffusion training progressing: **4.16 vs 4.12 loss** (minimal change from v1).

## Infrastructure
**Total cost: $40.35** across 23 spot sessions. Multiple spot reclaims caused training fragmentation, especially 3/9 afternoon (8 reclaims in 4 hours). Worst disruption: steps 19.3k-20.5k with 7 brief sessions. Recent stability: 8.5hr session completed 45.2k→50k without interruption.

Current session uptime: **1.3hrs** since boot, trainer idle post-completion.

## What's Next
**Training complete**. Execute v3 benchmarks: LAMBADA, WikiText-103, confidence analysis. Compare v1→v3 AR performance and S1 diffusion progress. **S1 accuracy plateau concerning** - investigate tokenization, loss scaling, or architectural constraints before v4.