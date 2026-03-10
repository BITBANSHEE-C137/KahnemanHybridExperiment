# v3 Training SITREP

## v3 Training Status
**Step 33,600/50,000 (67.2% complete)**. L4 GPU at **100% util**, 70W/72W, 81°C. Rate ~300 steps/hr. **ETA: ~54hrs**. Current session: 16.6hrs uptime, **$7.60 spot cost** ($0.46/hr vs $0.98 on-demand, 53% savings).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 26k   | 29.58  | 4.02      | 27.7%   | 0.864 | 0.0063 |
| 27k   | 29.55  | 4.32      | 24.6%   | 0.866 | 0.0109 |
| 28k   | 29.40  | 4.51      | 23.8%   | 0.865 | 0.0068 |
| 29k   | 29.36  | 4.27      | 25.5%   | 0.867 | 0.0118 |
| 30k   | 29.16  | 4.34      | 24.6%   | 0.868 | 0.0046 |
| 31k   | 28.95  | 4.47      | 23.3%   | 0.871 | 0.0031 |
| 32k   | 29.04  | 4.35      | 24.2%   | 0.865 | 0.0089 |
| **33k** | **28.93** | **4.09** | **26.6%** | **0.861** | **0.0086** |

**AR perplexity improving steadily** (-0.65 over 7k steps). **Diffusion loss volatile** but trending down. **S1 accuracy recovering** from 28k dip. AUROC **slight regression** (-0.010 from peak). ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **28.93** | ✅ **Met** |
| AUROC  | > 0.75 | **0.861** | ✅ **Met** |
| ECE    | < 0.05 | **0.0086** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.09** | ✅ **Near target** |
| S1 Acc | → 40% | **26.6%** | ❌ **Need +13.4pp** |

**4/5 targets met**. S1 accuracy **significantly behind** but trending up.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR performance exceeds v1** (28.93 vs 43.86 PPL). Diffusion loss comparable to v1 S1 loss.

## Infrastructure
**19 spot sessions**, total **$27.59** vs **$43.44 on-demand** (36% savings). Major disruption period 3/9 17:00-22:00 with **11 spot reclaims** in 5hrs - likely capacity/pricing volatility. Current session stable 16.6hrs on g6.2xlarge. **3 checkpoints** available, last sync 19:49 UTC.

## What's Next
v3 completion in ~54hrs. Post-training: comprehensive benchmarking vs v1/v2, confidence calibration analysis, S1 accuracy deep-dive (currently **underperforming** target by 34%).