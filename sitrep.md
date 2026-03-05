# v2 Training SITREP

## v2 Training Status
**Progress:** 15.5k/50k steps (**31%**) • **Rate:** ~400 steps/hr • **GPU:** 99% util, 52°C • **ETA:** ~88 hrs • **Current cost:** $0.44/hr spot (64% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 8k   | 27.58  | 4.65     | 21.1%   | 0.845 | 0.007 |
| 10k  | 28.39  | 4.37     | 25.1%   | 0.850 | 0.004 |
| 12k  | 29.35  | 4.34     | 25.6%   | 0.852 | 0.009 |
| 15k  | **31.05** | **4.33** | **26.1%** | **0.852** | **0.014** |

**Trends:** AR perplexity **degrading** (+13% since 8k). S1 accuracy **plateaued** at ~25-26%. Diffusion loss improving. ECE **regressing** (calibration worsening).

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.05** | ✅ **MET** |
| AUROC > 0.75 | **0.852** | ✅ **MET** |
| ECE < 0.05 | **0.014** | ✅ **MET** |
| Diff Loss → 4.0 | **4.33** | 🔄 Improving |
| S1 Acc → 40% | **26.1%** | ❌ Stalled |

**3/5 targets met.** S1 accuracy critically underperforming vs 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL.

Current v2 AR PPL (31.05) **better** than v1 WikiText baseline. S1 token accuracy tracking poorly vs v1's 67% loss reduction achievement.

## Infrastructure
**Current:** g5.2xlarge, us-east-1f, 2.3h uptime • **Spot stability:** 10 sessions, 6 reclaims in 24h (frequent interruptions) • **Total cost:** $10.92 across all sessions • **Checkpoint:** 15k saved (1.5GB)

## What's Next
**Immediate:** Monitor S1 accuracy stagnation - may need LR adjustment or architectural review. **Post-completion:** Full v2 benchmarks, confidence calibration analysis, v1 vs v2 head-to-head on standardized evals.