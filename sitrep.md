# v2 Training SITREP - Step 35,700

## v2 Training Status
**71.4%** complete (35,700/50k steps). A10G **100% utilized**, 196W/300W, 53°C. Current rate ~500 steps/hr. **ETA: 29 hours**. Spot cost **$4.27** current session, **$0.45/hr** (63% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 28000 | 31.32 | 3.95 | 28.2% | 0.872 | 0.007 |
| 29000 | 31.43 | 4.21 | 27.7% | 0.860 | 0.022 |
| 30000 | 31.68 | 4.08 | 28.1% | 0.864 | 0.023 |
| 31000 | 31.60 | 4.49 | 24.5% | 0.862 | 0.014 |
| 32000 | 31.39 | 3.96 | 28.4% | 0.871 | 0.013 |
| 33000 | 31.29 | 4.23 | 25.4% | 0.864 | 0.008 |
| 34000 | 31.13 | 4.68 | 22.0% | 0.854 | 0.009 |
| **35000** | **30.84** | **4.79** | **21.4%** | **0.855** | **0.011** |

**Trends**: AR PPL steadily improving ✓. **S1 accuracy regressing** badly (28% → 21%). Diff loss volatile, trending up. AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.84** | ✅ |
| AUROC | > 0.75 | **0.855** | ✅ |
| ECE | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.79** | ⚠️ |
| S1 Accuracy | → 40% | **21.4%** | ❌ |

**3/5 targets met**. Diffusion loss 20% above target. S1 accuracy **severely underperforming** - half the target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. v2 AR PPL (**30.84**) already better than v1 WikiText (43.86) and approaching GPT-2 baseline.

## Infrastructure
**13 sessions**, **$23.25 total cost**. Current session: 9.4hrs uptime, stable. Recent spot history clean - no reclaims since 3/5 19:52. Running us-east-1b, rate stable at $0.45/hr.

## What's Next
**Critical**: Investigate S1 token accuracy collapse - dropped 25% since step 28k. After completion: full v2 benchmarks, confidence calibration analysis, compare joint training impact vs v1.