# v3 Training SITREP

## v3 Training Status
**Step 43,200/50,000 (86.4%)** | GPU: 100% util, 72W/72W, 80°C | Rate: ~7.3 steps/min | **ETA: ~15.5 hrs** | Current spot: **$0.43/hr** (56.5% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 36000 | 28.59  | 4.46      | 23.5%  | 0.864 | 0.011 |
| 38000 | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 40000 | 28.27  | 3.76      | 30.3%  | **0.881** | 0.009 |
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43000 | **28.14** | 4.20      | 25.9%  | 0.869 | **0.010** |

**Trends:** AR PPL improving steadily (-1.6% over 7k steps). Diffusion loss volatile but trending down. **S1 accuracy peaked at 30.3% then regressed**. AUROC stable ~0.87. ECE excellent at 0.010.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.14** | ✅ **PASS** |
| AUROC > 0.75 | **0.869** | ✅ **PASS** |
| ECE < 0.05 | **0.010** | ✅ **PASS** |
| Diff loss → 4.0 | **4.20** | ⚠️ Close (5% over) |
| S1 accuracy → 40% | **25.9%** | ❌ Need +14.1pp |

**3/5 targets met**. S1 accuracy is lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v3 AR performance (28.14 PPL) already exceeds WikiText baseline**. S1 accuracy at 25.9% vs target 40%.

## Infrastructure
**21 spot interruptions** across 3 days, total cost **$34.76**. Current g6.2xlarge stable 5.7hrs. Instance churn mostly resolved - previous sessions had severe instability (9 reclaims on 3/9). **Cost efficiency: 56.5% savings maintained**.

## What's Next
6,800 steps remaining (~15hrs). **Focus: S1 accuracy regression analysis**. After completion: comprehensive v1 vs v3 benchmarks, confidence calibration deep-dive, production readiness assessment.