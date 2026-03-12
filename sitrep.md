# v3 Training SITREP

## v3 Training Status
**99.2% complete** (49.6k/50k steps). GPU at **99% utilization** (L4, 82°C, 16.6GB/23GB VRAM). Current rate ~5.3 steps/min, **ETA: 1.3 hours**. Spot cost: **$3.68** current session, **$4.00 projected** (53% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | 4.41      | **24.9%** | 0.867 | 0.012 |

**AR PPL stable ~28**. **S1 accuracy regressing** (29.3% → 24.9%). Diffusion loss volatile but trending up. Confidence metrics stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.05** | ✅ |
| AUROC > 0.75 | **0.867** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.41** | ❌ (10% over) |
| S1 accuracy → 40% | **24.9%** | ❌ (38% under) |

**3/5 targets met**. S1 performance concerning - **15% drop from peak**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. 

Current v3 AR performance (**PPL 28**) **beats v1** (43.86) and **matches GPT-2 baseline**. S1 regressing vs v1's 67% drop target.

## Infrastructure
Current: g6.2xlarge (L4) in us-east-1a, **7.9h uptime**. **22 spot sessions**, **$39.93 total cost**. Multiple reclaims early (steps 20k-21k), but **stable since step 24k**. No recent interruptions.

## What's Next
**400 steps remaining** (~1.3h). Monitor S1 accuracy regression. Post-completion: v3 benchmarks, confidence analysis, compare joint training impact vs v1/v2 baselines.