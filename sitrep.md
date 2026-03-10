# SITREP: v3 Training Status

## v3 Training Status
**Step 32,800/50,000 (65.6%)** - GPU fully utilized at 100% (NVIDIA L4, 80°C). Current spot rate **$0.46/hr** (53.1% savings). ETA ~15 hours at current pace. Total run cost: **$26.94**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 25000 | 29.48  | 4.08      | 26.5%  | 0.861 | 0.004 |
| 26000 | 29.58  | 4.02      | 27.7%  | 0.864 | 0.006 |
| 27000 | 29.55  | 4.32      | 24.6%  | 0.866 | 0.011 |
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865 | 0.007 |
| 29000 | 29.36  | 4.27      | 25.5%  | 0.867 | 0.012 |
| 30000 | 29.16  | 4.34      | 24.6%  | 0.868 | 0.005 |
| 31000 | 28.95  | 4.47      | 23.3%  | 0.871 | 0.003 |
| 32000 | 29.04  | 4.35      | 24.2%  | 0.865 | 0.009 |

**Trends**: AR perplexity gradually improving (29.48→29.04). Diffusion loss volatile around 4.3-4.5. **S1 accuracy stagnating ~24%**. AUROC peaked at 0.871 but regressed to 0.865. ECE unstable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.04** | ✅ |
| AUROC  | > 0.75 | **0.865** | ✅ |
| ECE    | < 0.05 | **0.009** | ✅ |
| Diff Loss | → 4.0 | **4.35** | 🔄 |
| S1 Acc | → 40% | **24.2%** | ❌ |

**3/5 targets met**. S1 accuracy significantly below target. Diffusion loss plateaued above 4.0.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% / PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR performance (29.04 PPL) matches GPT-2 baseline**, indicating no joint training degradation. S1 performance gap remains large.

## Infrastructure
**19 sessions**, heavy spot churn Mar 9-10 (14 interruptions). Stabilized on current g6.2xlarge since 04:25 UTC (15h uptime). Previous sessions averaged <3h due to aggressive spot reclaims. **Total cost efficiency: 53% savings vs on-demand**.

## What's Next
Complete v3 training (~15h remaining). **Priority**: analyze S1 token accuracy plateau - may need learning rate adjustment or architecture changes. Post-completion: comprehensive v1/v2/v3 benchmark comparison, confidence calibration analysis.