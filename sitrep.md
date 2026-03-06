# v2 Training SITREP

## v2 Training Status
**86.4% complete** (43,200/50,000 steps). A10G @ **99% GPU util**, 193W/300W limit, 50°C. Rate: ~1.4 steps/min. **ETA: 4.8 hours**. Spot rate: **$0.463/hr** (61.8% savings vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 36000 | 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 38000 | 30.44  | 4.28      | 26.7%  | 0.865 | 0.004 |
| 40000 | 30.21  | 4.56      | 23.2%  | 0.857 | 0.007 |
| 42000 | 30.08  | 4.07      | 29.0%  | 0.862 | 0.016 |
| 43000 | **29.96** | **3.93** | **29.2%** | **0.868** | **0.020** |

**Strong trends**: AR perplexity steadily improving (-2.4%), diffusion loss converging. **S1 accuracy volatile** but trending up. AUROC stable ~0.86. **ECE degrading** - confidence calibration worsening.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.96** | ✅ **PASS** |
| AUROC > 0.75 | **0.868** | ✅ **PASS** |
| ECE < 0.05 | **0.020** | ✅ **PASS** |
| Diff loss → 4.0 | **3.93** | ✅ **PASS** |
| S1 accuracy → 40% | **29.2%** | ❌ **MISS** |

**4/5 targets met**. S1 accuracy lagging significantly behind 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 AR already stronger** (29.96 vs 43.86 PPL). S1 performance needs validation against v1's 4.12 loss.

## Infrastructure
**15 spot sessions**, $27.63 total cost. Current session: 2.8hrs uptime, stable. Historical: frequent reclaims in 1b/1a zones, **1f zone most stable**. Cost tracking accurate, sync running.

## What's Next
6.8k steps remaining (~4.8hr). Post-completion: LAMBADA/WikiText benchmarks, v1/v2 head-to-head, **confidence calibration deep-dive** (ECE regression concerning). S1 accuracy investigation needed.