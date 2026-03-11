# v3 Training SITREP

## v3 Training Status
**Step 48,700/50,000** (97.4% complete). L4 GPU at **98% util**, 71W/72W power, 75°C. Training rate ~164 steps/hr. **ETA: 8 hours**. Current spot cost **$0.463/hr** (53% savings vs on-demand). Projected total: **$4.01**.

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 41k  | 28.30   | 3.949     | 27.8%   | 0.866 | 0.011 |
| 42k  | 28.33   | 3.892     | 29.1%   | 0.870 | 0.013 |
| 43k  | 28.14   | 4.196     | 25.9%   | 0.869 | 0.010 |
| 44k  | 28.07   | 4.404     | 24.9%   | 0.867 | 0.010 |
| 45k  | 27.95   | 4.159     | 26.5%   | 0.870 | 0.011 |
| 46k  | 28.13   | 3.943     | 28.1%   | 0.866 | 0.016 |
| 47k  | 28.09   | 3.883     | 29.3%   | 0.870 | 0.014 |
| **48k** | **28.04** | **4.192** | **26.1%** | **0.870** | **0.012** |

**Trends**: AR PPL stable ~28, slight improvement. Diffusion loss volatile (3.88-4.40). S1 accuracy oscillating 25-29%. AUROC consistent ~0.87. ECE well-controlled <0.016.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **28.04** | ✅ **Met** |
| AUROC  | > 0.75 | **0.870** | ✅ **Met** |  
| ECE    | < 0.05 | **0.012** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.192** | 🟡 **Close** |
| S1 Acc | → 40%  | **26.1%** | ❌ **Gap** |

**3/5 targets met**. S1 accuracy significantly below 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%/WikiText 29.07 PPL. **Current v3 AR performance (28.04 PPL) exceeds both v1 and approaching GPT-2 baseline**.

## Infrastructure  
**22 spot sessions**, total cost **$39.23**. Current L4 instance stable 6.5hrs. Previous session volatility 3/9-3/10 with multiple reclaims, but **stable since 3/11**. Strong cost efficiency vs on-demand.

## What's Next
Training completes in ~8hrs. **Immediate**: final checkpoint, comprehensive benchmarking vs v1/GPT-2. **Analysis focus**: S1 accuracy deficit investigation, confidence calibration assessment, diffusion convergence analysis.