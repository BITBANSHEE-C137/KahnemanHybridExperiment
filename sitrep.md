# v3 Training Status SITREP
*2026-03-12 12:51 UTC*

## v3 Training Status
**TRAINING COMPLETE** - 50,000/50,000 steps (100%). Current session idle on step 0 (likely post-completion cleanup). GPU underutilized at **38%** on L4 (27W/72W). Spot rate: **$0.42/hr** (57% savings vs on-demand).

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 28.14 | 4.196 | 25.9% | 0.869 | 0.010 |
| 44000 | 28.07 | **4.404** | 24.9% | 0.867 | 0.010 |
| 45000 | 27.95 | 4.159 | 26.5% | 0.870 | 0.011 |
| 46000 | 28.13 | **3.943** | **28.1%** | 0.866 | **0.016** |
| 47000 | 28.09 | **3.883** | **29.3%** | 0.870 | 0.014 |
| 48000 | 28.04 | 4.192 | 26.1% | 0.870 | 0.012 |
| 49000 | 28.05 | **4.407** | 24.9% | 0.867 | 0.012 |
| 50000 | **27.99** | 4.163 | 26.5% | **0.870** | 0.012 |

**Trends**: AR PPL slowly improving. Diffusion loss volatile (3.88-4.41). S1 accuracy peaked mid-training then regressed. AUROC stable ~0.87. ECE degraded slightly.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **4.163** | ❌ Missed by 4% |
| S1 accuracy → 40% | **26.5%** | ❌ **33% short** |

**3/5 targets met**. S1 accuracy significantly underperforming.

## v1 Benchmark Baseline
v1 final metrics: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**27.99**) substantially better than v1 (43.86). S1 performance unclear without loss comparison.

## Infrastructure
**25 sessions**, **$40.47** total cost. Extreme spot volatility - 13 interruptions on 3/9 alone. Recent stability: current session running 8min without interruption. g6.2xlarge preferred instance type. Average **56% spot savings**.

## What's Next
**IMMEDIATE**: v3 benchmarking on LAMBADA/WikiText-103. Compare v1→v3 improvements. **CONCERN**: S1 accuracy plateau suggests dual-process integration issues. Confidence head analysis critical for understanding AUROC/ECE performance vs accuracy disconnect.