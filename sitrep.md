# v3 Training Status SITREP

## v3 Training Status
**Step 29,500/50,000** (59% complete). GPU at **100% utilization** on L4 (81°C, 70W). Current rate ~300 steps/hr. **ETA: 28 hours**. Spot cost **$4.38** current session, **53.2% savings** vs on-demand.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 22000 | 29.70  | 3.95      | 28.3%  | 0.876 | 0.004  |
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.006  |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.005  |
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.004  |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.006  |
| 27000 | 29.55  | 4.32      | 24.6%  | 0.866 | 0.011  |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.007  |
| 29000 | 29.36  | 4.27      | 25.5%  | 0.867 | 0.012  |

**AR perplexity** plateaued ~29.4-29.7. **Diffusion loss** volatile 4.0-4.5 range. **S1 accuracy declining** 28.3%→25.5% (concerning). **AUROC stable** ~0.86-0.87. **ECE fluctuating** but acceptable.

## Target Scorecard
- ✅ **AR PPL < 40**: 29.36 (target met)
- ✅ **AUROC > 0.75**: 0.867 (target met)  
- ✅ **ECE < 0.05**: 0.012 (target met)
- ❌ **Diff loss → 4.0**: 4.27 (6.8% above target)
- ❌ **S1 accuracy → 40%**: 25.5% (36% below target)

**3/5 targets met**. S1 token accuracy **regressing badly**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**29.36 PPL**) significantly better than v1. S1 performance (**25.5% acc**) concerning vs v1's final state. Joint training showing AR gains but **S1 degradation**.

## Infrastructure
Current: g6.2xlarge spot ($0.46/hr, 53% savings). **19 spot reclaims** since start - highly unstable. Total cost **$24.37** across sessions. Multiple brief interruptions 3/9 evening (7 reclaims in 3hrs). Current session stable 9.5hrs.

## What's Next
**S1 token accuracy decline is critical issue** - investigate learning rate scheduling, loss weighting. Diffusion loss needs convergence toward 4.0. After completion: comprehensive v1/v3 comparison focusing on joint training trade-offs.