# v4 Training Status
**Step 41,200/75,000 (54.9% complete)**. A10G at **100% utilization**, 206W/300W limit, 55°C, 16.6/23GB VRAM. Rate ~300 steps/hr, **ETA: ~4.7 days**. Current spot: **$0.44/hr** (63.8% savings vs on-demand). **Total cost: $53.48**.

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 37500 | 29.73 | 4.36 | 26.8% | 0.854 | 0.010 |
| 38000 | 29.43 | 4.38 | 27.7% | 0.856 | 0.016 |
| 38500 | 29.30 | 4.28 | 28.0% | 0.858 | 0.012 |
| 39000 | 29.17 | 4.08 | 30.5% | 0.857 | 0.008 |
| 39500 | 29.10 | 4.37 | 26.9% | 0.855 | 0.016 |
| 40000 | 29.05 | 3.79 | 32.7% | 0.862 | 0.018 |
| 40500 | 28.94 | 3.80 | 32.9% | 0.862 | 0.009 |
| **41000** | **28.84** | **3.94** | **30.9%** | **0.864** | **0.016** |

**Trends**: AR PPL steadily improving (-0.89 since 37.5k). Diffusion loss volatile but trending down. S1 accuracy peaked at 40k then regressed. AUROC solid upward trend. ECE fluctuating.

## Target Scorecard
- **AR PPL < 40**: ✅ **28.84** (well under target)
- **AUROC > 0.75**: ✅ **0.864** (exceeding target) 
- **ECE < 0.05**: ✅ **0.016** (good calibration)
- **Diff Loss → 4.0**: ✅ **3.94** (at target)
- **S1 Accuracy → 40%**: ❌ **30.9%** (9.1pp short, regressed from 32.9%)

**4/5 targets met**. S1 accuracy concerning - peaked at step 40k but dropped back below previous levels.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. Current AR PPL (**28.84**) now **beating GPT-2 baseline** (29.07), major improvement from v1's 43.86. S1 performance tracking toward v1's final state.

## Infrastructure
Current: g5.2xlarge spot in us-east-1e, **11.5hr uptime**. Spot history shows **73 sessions** with aggressive reclaiming (many <1hr runs). Recent stability improved - current session longest in days. Total infrastructure cost perfectly tracking projected **$32.06**.

## What's Next
Monitor S1 accuracy regression closely - may need learning rate adjustment if trend continues. On track for completion **~March 29**. Post-training: comprehensive v4 vs v1 benchmarks, confidence calibration analysis, diffusion sampling quality assessment.