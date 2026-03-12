# v3 Training SITREP

## v3 Training Status
**TRAINING COMPLETE** - Model reached **step 50,000/50,000** (100%). Current instance idle with 0% GPU utilization on A10G. Instance uptime: 8.8h across 23 sessions. Current spot rate: **$0.48/hr** (60.7% savings vs on-demand).

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 43000| 28.14  | 4.20      | 25.9%   | 0.869 | 0.010 |
| 45000| 27.95  | 4.16      | 26.5%   | 0.870 | 0.011 |
| 47000| 28.09  | 3.88      | 29.3%   | 0.870 | 0.014 |
| 49000| 28.05  | 4.41      | 24.9%   | 0.867 | 0.012 |
| **50000**| **27.99** | **4.16** | **26.5%** | **0.870** | **0.012** |

**Trends**: AR perplexity stable ~28. Diffusion loss volatile (3.88→4.41). S1 accuracy peaked at 29.3% but regressed. AUROC/ECE stable and strong.

## Target Scorecard

| Target | Current | Met |
|--------|---------|-----|
| AR PPL < 40 | **27.99** | ✅ |
| AUROC > 0.75 | **0.870** | ✅ |
| ECE < 0.05 | **0.012** | ✅ |
| Diff loss → 4.0 | **4.16** | ❌ |
| S1 accuracy → 40% | **26.5%** | ❌ |

**3/5 targets met**. Diffusion loss 4% above target. S1 accuracy 34% below target.

## v1 Benchmark Baseline
v1 final metrics: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: 95.08% LAMBADA, 29.07 WikiText PPL. v3 shows **36% worse AR perplexity** vs GPT-2 baseline but **similar S1 performance** to v1.

## Infrastructure
Total cost: **$40.35** across 23 spot instances. Multiple spot reclaims caused training fragmentation (especially Mar 9). Current session stable for 8.8h. Instance types mixed: g5.2xlarge primary, g6.2xlarge secondary. **60.7% cost savings** vs on-demand.

## What's Next
Training complete - ready for **v3 benchmark evaluation**. Priority: LAMBADA/WikiText-103 comparison vs v1 baselines. Investigate diffusion loss volatility and S1 accuracy regression in final steps.