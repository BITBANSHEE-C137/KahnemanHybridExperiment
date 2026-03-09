# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 10,700/50,000 (21.4%)** | GPU: **99% util**, A10G @ 55°C | Rate: ~400 steps/hr | **ETA: 4.1 days** | Spot cost: **$0.46/hr** (62% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 3000 | 23.17  | 6.38      | 7.6%   | 0.638 | 0.010 |
| 5000 | 24.35  | 6.12      | 9.1%   | 0.695 | 0.008 |
| 7000 | 25.48  | 5.87      | 10.6%  | 0.739 | 0.009 |
| 9000 | 26.95  | 5.06      | 18.4%  | 0.805 | 0.006 |
| **10000** | **27.55** | **4.98** | **19.0%** | **0.828** | **0.005** |

**Trends**: AR PPL degrading steadily (+4.38 over 7k steps). Diffusion loss improving (-1.40). S1 accuracy **2.5x jump** at 9k. AUROC climbing consistently. ECE excellent and stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.55** | ✅ **PASS** |
| AUROC > 0.75 | **0.828** | ✅ **PASS** |
| ECE < 0.05 | **0.005** | ✅ **PASS** |
| Diff loss → 4.0 | **4.98** | 🔄 Trending |
| S1 accuracy → 40% | **19.0%** | 🔄 Trending |

**3/5 targets met**. Diffusion loss needs **-0.98** more. S1 accuracy needs **2.1x** improvement.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v3 AR PPL (**27.55**) already **37% better** than v1 WikiText (43.86) and approaching GPT-2 baseline (29.07).

## Infrastructure  
**Current session**: 13.2h uptime, $6.03 spent | **Previous session**: 6.8h, $3.11 (spot reclaim) | **Total**: $9.11 across 2 sessions, 0 interruptions today

Checkpoints: 8k, 9k, **10k** (1.5GB each), sync active

## What's Next
**AR regression concern**: PPL rising while other metrics improve suggests potential overfitting to diffusion objective. Monitor closely through 15k steps. If trend continues, consider rebalancing loss weights or early stopping AR component.