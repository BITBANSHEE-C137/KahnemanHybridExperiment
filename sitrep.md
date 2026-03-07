# v2 Training SITREP - 2026-03-07 01:00 UTC

## v2 Training Status
**Step 46,900/50,000** (93.8% complete) | GPU: 100% util, 196W/300W | **ETA: ~7 hours** | Current spot rate: **$0.46/hr** (61.8% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 39000 | 30.41  | 3.80      | 30.7%  | 0.863 | 0.007 |
| 42000 | 30.08  | 4.07      | 29.0%  | 0.862 | 0.016 |
| 45000 | 29.80  | 3.86      | 29.3%  | **0.875** | 0.016 |
| **46000** | **29.74** | **4.15** | **26.2%** | **0.865** | **0.011** |

**Trends**: AR perplexity steadily improving. Diffusion loss volatile but trending toward target. **S1 accuracy regressing** (30.7%→26.2%). AUROC peaked at step 45k, slight decline. ECE improved significantly.

## Target Scorecard
- ✅ **AR PPL < 40**: 29.74 (BEAT by 25%)
- ✅ **AUROC > 0.75**: 0.865 (BEAT by 15%)  
- ✅ **ECE < 0.05**: 0.011 (BEAT by 78%)
- ❌ **Diff loss → 4.0**: 4.15 (4% above target)
- ❌ **S1 accuracy → 40%**: 26.2% (35% below target)

**3/5 targets met**. S1 accuracy is concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**v2 shows AR improvement** (29.74 vs 43.86 PPL) but **S1 performance degraded** vs v1.

## Infrastructure
**15 spot sessions**, 7.3hr uptime current instance | Total cost: **$29.71** (62% savings) | **14 spot reclaims** in 3 days - high churn but recovering well | Latest checkpoint: 1.5GB @ step 46k

## What's Next
Complete v2 in ~7hrs → Full benchmark suite → **Investigate S1 accuracy regression** → Confidence head analysis → v1 vs v2 head-to-head comparison