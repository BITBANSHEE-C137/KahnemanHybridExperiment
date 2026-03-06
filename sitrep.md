# SITREP: v2 Training Status

*Date: 2026-03-06 18:00 UTC*

## v2 Training Status
**82.2%** complete (41,100/50,000 steps). A10G at **99% util**, 193W draw, 51°C. Rate: ~194 steps/hr. **ETA: 1.9 days**. Current spot: **$0.46/hr** (62% savings), total cost **$26.47**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 34000 | 31.13  | 4.68      | 22.0%  | 0.854 | 0.0086 |
| 35000 | 30.84  | 4.79      | 21.4%  | 0.855 | 0.0109 |
| 36000 | 30.69  | **4.30**  | **24.8%** | 0.863 | 0.0100 |
| 37000 | 30.65  | 4.75      | 21.6%  | 0.861 | 0.0069 |
| 38000 | 30.44  | **4.28**  | **26.7%** | 0.865 | **0.0042** |
| 39000 | 30.41  | **3.80**  | **30.7%** | 0.863 | 0.0068 |
| 40000 | 30.21  | 4.56      | 23.2%  | 0.857 | 0.0072 |
| 41000 | **30.12** | 4.47   | 25.1%  | 0.862 | 0.0123 |

**Trends**: AR PPL steadily improving. Diff loss volatile but trending down. S1 accuracy peaked at 39k (30.7%) then regressed. AUROC stable ~0.86. ECE increased last eval.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **30.12** | ✅ **MET** |
| AUROC  | > 0.75 | **0.862** | ✅ **MET** |
| ECE    | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.47** | 🔶 **CLOSE** |
| S1 Acc | → 40% | **25.1%** | ❌ **BEHIND** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 AR performance superior to v1** (30.12 vs 43.86 PPL). S1 loss comparable.

## Infrastructure
15 spot sessions, **$26.43 total**. Current g5.2xlarge stable 18min, no recent reclaims. Historical: 3 brief interruptions on 3/4, longest session 16hrs. **Excellent spot stability** in us-east-1b.

## What's Next
**8,900 steps remaining** (~46hrs). Watch S1 accuracy regression - may need LR adjustment. Post-completion: benchmark suite, confidence calibration analysis, v1/v2 head-to-head comparison on reasoning tasks.