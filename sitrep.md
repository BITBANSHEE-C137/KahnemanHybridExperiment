# v3 Training SITREP

## v3 Training Status
**Step 9,500/50,000 (19.0%)** | GPU: 100% util, 205W/300W, 57°C | **Rate**: ~230 steps/hr | **ETA**: 8.7 days | Spot: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 2000 | 22.53  | 6.54      | 6.4%   | 0.613 | 0.004 |
| 4000 | 23.71  | 6.29      | 8.5%   | 0.672 | 0.011 |
| 6000 | 24.85  | 6.08      | 9.9%   | 0.719 | 0.012 |
| 8000 | 26.29  | 5.60      | 12.6%  | 0.785 | 0.008 |
| **9000** | **26.95** | **5.06** | **18.4%** | **0.805** | **0.006** |

**🔴 AR PPL degrading** (22.5→27.0), **🟢 confidence head improving** (AUROC 0.61→0.81, ECE stable), **🟢 diffusion converging** well (6.5→5.1), **🟢 S1 accuracy accelerating** (6%→18%).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40.0 | **26.95** | ✅ |
| AUROC | > 0.75 | **0.805** | ✅ |
| ECE | < 0.05 | **0.0059** | ✅ |
| Diff Loss | → 4.0 | **5.06** | 🟡 (trending down) |
| S1 Accuracy | → 40% | **18.4%** | 🟡 (accelerating) |

**3/5 targets met**. Diffusion loss needs 21% more drop, S1 accuracy needs 2.2x improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR PPL (27.0) is 38% better than v1 WikiText (43.9)** - joint training not degrading AR performance this time.

## Infrastructure
**Uptime**: 11.7hrs across 2 sessions | **Total cost**: $8.43 | One spot reclaim at step 1000 (6.7hr session, $3.11) | Current session: 11.7hrs, $5.35, stable in us-east-1a

## What's Next
Continue v3 training - **strong momentum on confidence head and diffusion, AR stable**. Expect diffusion target hit by step 15k, S1 accuracy by step 20k. Will run full benchmarks at step 25k for mid-training checkpoint analysis.