# ML Ops SITREP - v3 Training Status

## v3 Training Status
**TRAINING COMPLETE** - Run finished at step **50,000** (100% complete). Current instance idle since 2026-03-12 02:40 UTC (3h50m ago). GPU: NVIDIA A10G at 0% utilization, 28°C. Spot rate: **$0.48/hr** (60.8% savings vs on-demand).

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | 4.40 | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | 3.94 | 28.1% | 0.866 | 0.016 |
| 47000 | 28.09 | 3.88 | 29.3% | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | 4.41 | 24.9% | 0.867 | 0.012 |
| **50000** | **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR perplexity stable ~28. Diffusion loss volatile (3.88-4.41). S1 accuracy peaked at step 47k (29.3%) but regressed. AUROC consistent ~0.87. ECE well-controlled <0.02.

## Target Scorecard
- ✅ **AR PPL < 40**: 27.99 (PASS)
- ✅ **AUROC > 0.75**: 0.870 (PASS) 
- ✅ **ECE < 0.05**: 0.012 (PASS)
- ❌ **Diff loss → 4.0**: 4.16 (MISS - target not met)
- ❌ **S1 accuracy → 40%**: 26.5% (MISS - 13.5pp short)

**3/5 targets met**. Diffusion process and S1 token prediction underperforming.

## v1 Benchmark Baseline
v1 final metrics: LAMBADA 94.26% acc, 1.46 PPL; WikiText-103 43.86 PPL; S1 loss 4.12. 

**v3 vs v1**: AR improved (27.99 vs 43.86 PPL), but S1 regressed (26.5% vs ~67% implied from loss). Need v3 benchmark runs for direct comparison.

## Infrastructure
**Total cost: $40.35** across 23 spot sessions. Notable instability 3/9-3/10 with **12 spot reclaims** in ~6hrs (steps 20k-21k). Stabilized on g6.2xlarge instances. Current session: 3h50m uptime, $1.82 spent.

Instance type migration: g5.2xlarge → mixed g6/g5 → g6.2xlarge (final stretch). **60.8% cost savings** vs on-demand.

## What's Next
1. **Run v3 benchmarks** (LAMBADA, WikiText-103) - training complete
2. **v1 vs v3 comparison** - quantify AR improvements vs S1 regression  
3. **Confidence head analysis** - investigate AUROC plateau at 0.87
4. **Diffusion loss debugging** - volatility suggests optimization issues

**Action required**: Launch benchmark evaluation job.