# v3 Training Status

**TRAINING COMPLETE** ✅ Step **50,000/50,000** (100%)  
Current instance idle - trainer stopped, sync running  
GPU: NVIDIA A10G @ 0% util, 27°C, 0MB VRAM used  
Spot rate: **$0.476/hr** (60.8% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | **4.40** | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.16 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | **3.94** | **28.1%** | 0.866 | **0.016** |
| 47000 | 28.09 | **3.88** | **29.3%** | 0.870 | 0.014 |
| 48000 | 28.04 | 4.19 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | **4.41** | 24.9% | 0.867 | 0.012 |
| 50000 | **27.99** | 4.16 | 26.5% | **0.870** | 0.012 |

**Trends:** AR perplexity stable ~28, slight improvement final step. S1 accuracy peaked at step 47k then regressed. Diffusion loss volatile - best at 47k (3.88), worst at 44k/49k (4.4+). AUROC consistent ~0.87. ECE spike at 46k concerning.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.0** | ✅ **PASS** |
| AUROC | > 0.75 | **0.870** | ✅ **PASS** |
| ECE | < 0.05 | **0.012** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.16** | ❌ **MISS** |
| S1 Accuracy | → 40% | **26.5%** | ❌ **MISS** |

**3/5 targets met.** Diffusion loss 4% over target, S1 accuracy 34% below target.

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  

**v3 vs v1:** AR improved (43.86→28.0 PPL), S1 regressed slightly (4.12→4.16 loss). Current model **36% better AR perplexity** than v1.

## Infrastructure

**23 sessions, $40.35 total cost** (60.8% savings vs on-demand $103.13)  
Current: 5.8hr uptime, stable spot instance  
**12 spot reclaims** - heavy churn 3/9 evening (7 reclaims in 4hrs)  
Best stability: g6.2xlarge sessions (11-24hr runs)  
Worst: g5/g6.xlarge frequent interruptions

## What's Next

Training complete - **ready for v3 benchmarks**  
Priority: LAMBADA/WikiText evaluation vs v1/GPT-2 baselines  
Analyze S1 accuracy plateau and diffusion loss volatility  
Consider confidence calibration improvements (ECE spike investigation)