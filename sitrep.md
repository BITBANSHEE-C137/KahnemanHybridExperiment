# v3 Training SITREP

## v3 Training Status
**Step 1600/50000 (3.2%)** | GPU: 100% util, 59°C, 70% VRAM | Rate: ~229 steps/hr | **ETA: 9.1 days** | Spot cost: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | **21.29** | 6.75 | 5.04% | 0.557 | 0.006 |

**Single eval checkpoint** - no trend analysis possible yet. Need more data points.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **21.29** | ✅ **MET** |
| AUROC > 0.75 | **0.557** | ❌ **-0.19** |
| ECE < 0.05 | **0.006** | ✅ **MET** |
| Diff loss → 4.0 | **6.75** | ❌ **+2.75** |
| S1 accuracy → 40% | **5.04%** | ❌ **-35%** |

**2/5 targets met.** AUROC severely underperforming, S1 accuracy abysmal.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR PPL (**21.29**) already **51% better** than v1 WikiText baseline. Confidence calibration excellent (ECE 0.006 vs typical 0.05+). However, AUROC catastrophically low - confidence head not learning discriminative features.

## Infrastructure
**2 spot sessions, 1 reclaim.** Session 1: 6.8hrs, $3.11 (steps 400-1000). Current session 2: 2.2hrs uptime, $0.95. **Total cost: $4.07**. Stable g5.2xlarge spot at 62% discount. No current issues.

## What's Next
**Critical:** Investigate AUROC collapse - confidence head may need architecture/loss rebalancing. S1 token accuracy trending toward random performance needs immediate attention. Next eval at step 2000 will determine if joint training is fundamentally broken or just needs more steps.