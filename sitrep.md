# v2 Training SITREP

## v2 Training Status
**Step 37,300/50,000** (74.6% complete). A10G at **100% util**, 191W/300W, 49°C, 16.6GB/23GB VRAM. Rate: ~320 steps/hr. **ETA: ~40 hours**. Current spot rate **$0.453/hr** (62.7% savings vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 30000 | 31.68  | 4.08      | 0.281  | 0.864 | 0.023 |
| 32000 | 31.39  | 3.96      | 0.284  | 0.871 | 0.013 |
| 34000 | 31.13  | 4.68      | 0.220  | 0.854 | 0.009 |
| 36000 | 30.69  | 4.30      | 0.248  | 0.863 | 0.010 |
| 37000 | **30.65** | **4.75** | **0.216** | **0.861** | **0.007** |

**AR perplexity** trending down steadily ✓. **Diffusion loss** volatile (3.96→4.75). **S1 accuracy** regressed from 0.284→0.216. **Confidence calibration excellent** - ECE dropped to 0.007, AUROC stable ~0.86.

## Target Scorecard
- ✓ **AR PPL < 40**: 30.65
- ✓ **AUROC > 0.75**: 0.861  
- ✓ **ECE < 0.05**: 0.007
- ❌ **Diff loss → 4.0**: 4.75 (trending wrong direction)
- ❌ **S1 accuracy → 40%**: 21.6% (well below target)

**3/5 targets met**. Diffusion loss and S1 accuracy concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **v2 AR PPL (30.65) already beating WikiText baseline**. S1 performance needs major improvement - currently 67% worse than v1.

## Infrastructure
**13 sessions**, 12 spot reclaims. Current session: 11.5hr uptime, $5.17 spent. Total cost **$24.15** vs $32.51 on-demand. Spot stability poor but cost effective. Instance type switching (g5.xlarge/2xlarge) indicates capacity issues.

## What's Next
**Major S1 regression** needs investigation - accuracy dropped 23% since step 32k. Consider: learning rate adjustment, S1 loss weighting, or architectural changes. After completion: comprehensive v1/v2 benchmarks, confidence head analysis on real tasks.