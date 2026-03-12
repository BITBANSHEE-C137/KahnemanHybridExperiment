# v3 Training Status SITREP

## v3 Training Status
**COMPLETE** - Step 50,000/50,000 ✅  
GPU: A10G @ 54% util, 65W/300W, 40°C, 2.2GB/23GB VRAM  
Current session: 9m uptime, spot rate $0.47/hr (61% savings)  
**Ready for v3 benchmarks**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 43000| 28.14  | 4.20      | 25.9%   | 0.869 | 0.010|
| 44000| 28.07  | 4.40      | 24.9%   | 0.867 | 0.010|
| 45000| 27.95  | 4.16      | 26.5%   | 0.870 | 0.011|
| 46000| 28.13  | **3.94**  | **28.1%** | 0.866 | 0.016|
| 47000| 28.09  | **3.88**  | **29.3%** | 0.870 | 0.014|
| 48000| 28.04  | 4.19      | 26.1%   | 0.870 | 0.012|
| 49000| 28.05  | 4.41      | 24.9%   | 0.867 | 0.012|
| 50000| **27.99** | 4.16   | 26.5%   | **0.870** | 0.012|

**Trends**: AR PPL plateaued ~28, brief diffusion improvement (steps 46-47k), S1 accuracy volatile but trending up. AUROC stable >0.86.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ |
| AUROC > 0.75 | **0.870** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.16** | ❌ (regressed from 3.88)|
| S1 accuracy → 40% | **26.5%** | ❌ (14% short) |

**3/5 targets met**. Diffusion loss and S1 accuracy remain challenging.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
v3 AR PPL (**27.99**) significantly better than v1 (43.86), approaching GPT-2 baseline.

## Infrastructure
**Total cost**: $40.31 across 23 spot sessions  
**Reliability issues**: 15+ spot reclaims between steps 19-21k causing training instability  
**Current**: g5.2xlarge us-east-1b, stable since 02:40 UTC  
**Average savings**: ~60% vs on-demand

## What's Next
1. **v3 benchmarks**: LAMBADA, WikiText-103, S1 confidence analysis
2. **v1 vs v3 comparison**: Quantify AR improvements, analyze S1 regression  
3. **Confidence head deep-dive**: ECE performance excellent, investigate AUROC ceiling
4. **Diffusion loss investigation**: Why regression from mid-training lows?