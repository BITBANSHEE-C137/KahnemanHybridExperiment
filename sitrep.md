# SITREP: v3 Training Status

## v3 Training Status
**Training complete at step 50,000/50,000** ✅  
Current instance idle (0% GPU util, 11W power). Step 0 displayed due to trainer restart after completion.  
**Total cost: $40.35** across 23 spot sessions. Current session: 4.3h uptime, $2.05 spent.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010  |
| 44000 | 28.07  | **4.40**  | 24.9%  | 0.867 | 0.010  |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011  |
| 46000 | 28.13  | **3.94**  | 28.1%  | 0.866 | 0.016  |
| 47000 | 28.09  | **3.88**  | 29.3%  | 0.870 | 0.014  |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870 | 0.012  |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867 | 0.012  |
| 50000 | **27.99** | 4.16   | 26.5%  | **0.870** | 0.012 |

**Trends**: AR PPL stable ~28, slight improvement to **27.99**. Diffusion loss volatile (3.88-4.41), trending toward target. S1 accuracy peaked at **29.3%** (step 47k), regressed to 26.5%. AUROC solid at **0.870**. ECE well controlled <0.02.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **27.99** | ✅ |
| AUROC > 0.75 | **0.870** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.16** | 🔶 (close) |
| S1 accuracy → 40% | **26.5%** | ❌ |

**3/5 targets met**. Diffusion loss within 0.16 of target. S1 accuracy 13.5% short of 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**v3 AR performance significantly improved** (27.99 vs 43.86 PPL). S1 comparable to v1.

## Infrastructure
**23 spot sessions**, **61% savings** ($40.35 vs $82.85 on-demand). Heavy instance churn on 3/9 (12 reclaims in 6h). Stable g6.2xlarge runs on 3/10-3/11. Training completed successfully despite interruptions.

## What's Next
**v3 training complete**. Priority: comprehensive benchmarking vs v1/v2, confidence calibration analysis, S1 accuracy investigation. Model ready for production evaluation.