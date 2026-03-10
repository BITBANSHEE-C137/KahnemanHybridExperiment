# v3 Training SITREP

## v3 Training Status
**Step 24,500/50,000 (49%)** | L4 GPU @ **100% util** | **$0.46/hr spot** (53% savings) | **1.07 hrs uptime** | ETA: ~26 hrs | **$20.21 projected**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008  |
| 18000 | 28.99  | 4.44      | 23.0%  | 0.858 | 0.010  |
| 19000 | 29.21  | 4.39      | 22.1%  | 0.866 | 0.011  |
| 20000 | 29.22  | 4.24      | 26.8%  | 0.857 | 0.005  |
| 21000 | 29.94  | 4.26      | 26.8%  | 0.856 | 0.012  |
| 22000 | 29.70  | **3.95**  | 28.3%  | **0.876** | **0.004** |
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.006  |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.005  |

**Trends**: AR PPL stable ~29. **Diff loss volatile** (3.95→4.31). S1 accuracy **stagnant** ~25%. AUROC peaked at step 22000. **No clear convergence**.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **29.5** | ✅ |
| AUROC  | > 0.75 | **0.862** | ✅ |
| ECE    | < 0.05 | **0.005** | ✅ |
| Diff Loss | → 4.0 | **4.31** | ❌ |
| S1 Acc | → 40% | **25.2%** | ❌ |

**2/5 targets failing**. Diff loss regressing, S1 accuracy **15% below target**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: 95.08%/29.07 PPL. **v3 AR quality matches GPT-2 baseline** but S1 system underperforming vs v1.

## Infrastructure
**19 spot sessions**, avg **$0.52/hr**. **Heavy churn** Mar 9 (12 reclaims in 4hrs). Current g6.2xlarge stable 1hr+. Total: **$20.49 spent**.

## What's Next
Monitor diff loss volatility. **S1 accuracy plateau concerning** - may need LR adjustment or architecture review. Next eval at 25k steps critical for trajectory assessment.