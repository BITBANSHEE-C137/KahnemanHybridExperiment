# v3 Training SITREP

## v3 Training Status
**Step 31,300/50,000 (62.6%)** | L4 GPU @ **100% util** (71°C, 16.6GB VRAM) | **18,700 steps remaining** | Current rate ~240 steps/hr | **ETA: ~78hrs** | Spot rate **$0.46/hr** (53% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 24000| 29.53  | 4.31      | 25.2%   | 0.862 | 0.0055|
| 26000| 29.58  | 4.02      | 27.7%   | 0.864 | 0.0063|
| 28000| 29.40  | 4.51      | 23.8%   | 0.865 | 0.0068|
| 30000| 29.16  | 4.34      | 24.6%   | 0.868 | 0.0046|
| **31000**| **28.95** | **4.47** | **23.3%** | **0.871** | **0.0031**|

**Trends:** AR PPL improving steadily (-0.58 since 24k). AUROC climbing (+0.009). ECE volatile but trending better. **Diff loss plateaued ~4.3-4.5**. S1 accuracy **regressing** (-1.9% since 26k).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **28.95** | ✅ **MET** |
| AUROC | > 0.75 | **0.871** | ✅ **MET** |
| ECE | < 0.05 | **0.0031** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.47** | ❌ Stalled |
| S1 Accuracy | → 40% | **23.3%** | ❌ **Regressing** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR performance approaching GPT-2 baseline** (28.95 vs 29.07 PPL).

## Infrastructure
Current session: **g6.2xlarge** running **12.6hrs** (step 24900→31300). **19 total sessions**, heavy spot reclaims 3/9 (step ~20k instability). Total cost **$25.79** vs $43.33 on-demand (**40% savings**). Infrastructure stable since 3/10 04:25 UTC.

## What's Next
**S1 accuracy regression** needs investigation - down from 27.7% peak. Diff loss **stuck above 4.4** for 7k steps. Consider **LR schedule adjustment** or **S1 loss weighting**. Continue monitoring confidence calibration - ECE performance excellent.