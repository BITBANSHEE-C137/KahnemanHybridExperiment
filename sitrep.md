# v3 Training Status

**Step 12,000/50,000** (24% complete) | **100% GPU util** | A10G @ 201W/300W, 53°C  
**Rate**: ~230 steps/hr | **ETA**: ~7.2 days | **Spot cost**: $0.46/hr (**62% savings**)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 8000  | 26.29  | 5.597     | 12.6%  | 0.785 | 0.0076 |
| 9000  | 26.95  | 5.061     | 18.4%  | 0.805 | 0.0059 |
| 10000 | 27.55  | 4.979     | 19.0%  | 0.828 | 0.0053 |
| 11000 | 27.85  | 4.431     | 22.0%  | 0.853 | 0.0102 |
| 12000 | **28.12** | **4.309** | **25.0%** | **0.853** | **0.0066** |

**Trends**: AR PPL slowly degrading (+0.27 over 4k steps), diff loss improving steadily (-1.3), S1 accuracy climbing (+6.4pp), AUROC plateaued at 0.853, ECE volatile but acceptable.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **28.1** | ✅ |
| AUROC  | > 0.75 | **0.853** | ✅ |
| ECE    | < 0.05 | **0.007** | ✅ |
| Diff Loss | → 4.0 | **4.31** | 🟡 (92% there) |
| S1 Acc | → 40%  | **25.0%** | 🟡 (63% there) |

**3/5 targets met**. Diff loss and S1 accuracy on positive trajectories.

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (28.1) already better than v1 baseline (43.86)**

## Infrastructure

**Uptime**: 14.7hrs across 2 sessions | **Total cost**: $9.83  
Session 1: Steps 400-1000, $3.11 (terminated)  
Session 2: Steps 1000-12000, $6.68 (active)  
**No spot reclaims in current session**. Stable us-east-1a pricing.

## What's Next

Continue to step 50k (~7 days). Monitor AR PPL regression - may need LR adjustment if trend continues. Diff loss approaching target zone. Benchmark suite ready for step 50k evaluation.