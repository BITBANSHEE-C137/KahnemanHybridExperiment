# v3 Training SITREP

## v3 Training Status
**Step 20,400/50,000** (40.8% complete) on g5.xlarge A10G. **98% GPU util**, 197W/300W power, 56°C. Current rate ~11.6 steps/min. **ETA: ~42 hours**. Spot rate $0.44/hr (**56% savings** vs on-demand).

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|-------------|------------|----------|
| 13000 | 28.41  | 4.42      | 24.1%       | 0.844      | 0.011    |
| 14000 | 28.51  | 4.29      | 24.7%       | 0.852      | 0.009    |
| 15000 | 28.64  | 4.50      | 23.7%       | **0.864**  | **0.005** |
| 16000 | 28.66  | 4.38      | 23.5%       | 0.856      | 0.010    |
| 17000 | 28.89  | 4.34      | **25.2%**   | 0.858      | 0.008    |
| 18000 | 28.99  | 4.44      | 23.0%       | 0.858      | 0.010    |
| 19000 | 29.21  | 4.39      | 22.1%       | 0.866      | 0.011    |
| 20000 | 29.22  | **4.24**  | **26.8%**   | 0.857      | **0.005** |

**Concerning trends**: AR perplexity slowly degrading (28.4→29.2). S1 accuracy volatile but latest spike to 26.8% encouraging. Confidence metrics stable around targets.

## Target Scorecard
- ❌ **AR PPL < 40**: 29.22 (✓ met, improving trend needed)
- ✅ **AUROC > 0.75**: 0.857 
- ✅ **ECE < 0.05**: 0.005
- ❌ **Diff loss → 4.0**: 4.24 (close, trending down)
- ❌ **S1 accuracy → 40%**: 26.8% (67% of target)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**PPL 29.2**) significantly better than v1's WikiText baseline. S1 accuracy (26.8%) vs v1's effective ~35% from loss 4.12.

## Infrastructure
**15 spot interruptions** in 3 days, burning through instance types (g5→g6 cycling). Total cost **$16.55** across sessions. Current session: 40min uptime, stable. **Chronic spot instability** impacting training velocity - lost ~6 hours to restarts.

## What's Next
Training velocity concerning due to spot churn. Consider reserved capacity or higher spot bids. At current pace, **v3 completion ~March 11**. Priority: stabilize infrastructure, then analyze S1 accuracy volatility patterns.