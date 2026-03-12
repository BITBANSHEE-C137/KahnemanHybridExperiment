# v3 Training Status SITREP

## v3 Training Status
**COMPLETE** - Training finished at step **50,000/50,000** (100%). Current instance idle (0% GPU util, 11W power). A10G on g5.2xlarge spot @ **$0.48/hr** (61% savings vs on-demand). Instance uptime: 3.3hrs, cost: **$1.58**.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|---------|-----------|--------|-------|-------|
| 43000 | 28.14   | 4.196     | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07   | 4.404     | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95   | 4.159     | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13   | 3.943     | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09   | 3.883     | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04   | 4.192     | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05   | 4.407     | 24.9%  | 0.867 | 0.012 |
| 50000 | 27.99   | 4.163     | 26.5%  | 0.870 | 0.012 |

**Trends**: AR PPL stable ~28, slight improvement in final steps. Diff loss volatile 3.9-4.4 range. S1 accuracy peaked at step 47k (29.3%) then regressed. AUROC steady ~0.87. ECE well-controlled <0.02.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.163** | ❌ **MISS** (+4%) |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** (-34%) |

**3/5 targets achieved**. Diffusion loss close but unstable. S1 accuracy significantly below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. 

v3 vs v1: **AR PPL improved** 43.86→27.99 (-36%), **diff loss similar** 4.12→4.16. S1 token accuracy comparison pending v3 benchmarks.

## Infrastructure
**Total project cost: $40.35** across 23 spot instances. Multiple reclaims 3/9-3/10 (step 19k-20k range) caused training delays. Stable run 3/10-3/12 completed final 25k steps. Current instance stable 3.3hrs, sync/trainer running.

## What's Next
**v3 benchmarking**: LAMBADA, WikiText-103 evaluation. Compare v1→v3 AR improvements vs S1 regression. Analyze confidence head calibration at 0.87 AUROC. Target diffusion loss stabilization in v4.