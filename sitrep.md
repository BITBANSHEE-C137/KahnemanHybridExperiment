# v3 Training Status SITREP

## v3 Training Status
**TRAINING COMPLETE** - 50k/50k steps (**100%**)  
Current instance: g6.2xlarge (L4, 48% util, 4.2GB/23GB VRAM)  
Rate: N/A (training finished)  
Spot cost: **$0.42/hr** (57% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | 4.40 | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | 3.94 | 28.1% | 0.866 | 0.016 |
| 47000 | 28.09 | 3.88 | 29.3% | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | 4.41 | 24.9% | 0.867 | 0.012 |
| **50000** | **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR PPL plateaued ~28, diff loss volatile around 4.0-4.4, S1 accuracy oscillating 25-29%, AUROC stable ~0.87, ECE well-controlled <0.016.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy significantly underperforming (26.5% vs 40% target).

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**v3 vs v1**: AR improved (27.99 vs 43.86 PPL), diff performance similar (4.16 vs 4.12)

## Infrastructure
Total cost: **$40.39** across 24 spot sessions  
**23 spot reclaims** - severe instability Mar 9-10  
Current session: 9min uptime, stable on g6.2xlarge  
Major interruption period: 15+ reclaims in 6hrs on Mar 9

## What's Next
✅ **v3 training complete**  
🔄 Run full benchmark suite (LAMBADA, WikiText-103)  
🔍 Analyze S1 accuracy underperformance vs target  
📊 Compare v1→v3 improvements on standardized evals  
🧠 Deep-dive confidence calibration analysis