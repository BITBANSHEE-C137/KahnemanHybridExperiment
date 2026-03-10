# v3 Training SITREP

## v3 Training Status
**Step 30,100/50,000 (60.2%)** | GPU: **100% util** L4 @ 82°C | Rate: ~2.8 steps/min | **ETA: ~4.9 days** | Spot: **$0.46/hr** (-53% vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 23000 | 29.57 | 4.19 | 26.1% | 0.861 | 0.0059 |
| 25000 | 29.48 | 4.08 | 26.5% | 0.861 | 0.0042 |
| 27000 | 29.55 | 4.32 | 24.6% | 0.866 | 0.0109 |
| 29000 | 29.36 | 4.27 | 25.5% | 0.867 | 0.0118 |
| **30000** | **29.16** | **4.34** | **24.6%** | **0.868** | **0.0046** |

**Trends:** AR PPL gradually improving (**-1.4%** since 23k). AUROC steady climb (**+0.007**). S1 accuracy volatile, currently regressed. ECE erratic but acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.16** | ✅ **Met** |
| AUROC > 0.75 | **0.868** | ✅ **Met** |
| ECE < 0.05 | **0.0046** | ✅ **Met** |
| Diff loss → 4.0 | **4.34** | ⚠️ **91% there** |
| S1 accuracy → 40% | **24.6%** | ❌ **62% there** |

**3/5 targets met.** S1 accuracy **stuck at ~25%** - needs investigation.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**29.16 PPL**) significantly better than v1 (43.86), approaching GPT-2 baseline (29.07).

## Infrastructure
**19 spot sessions** across g5/g6 instances. **$24.83 total cost** (53% savings). Current g6.2xlarge stable **10.6hrs uptime**. Previous sessions show **frequent reclaims** (9-39min typical) - migration overhead impacting training efficiency.

## What's Next
Continue to 50k steps (~5 days). **Priority:** Analyze S1 accuracy plateau - may need LR schedule adjustment or architectural review. Post-completion: v3 benchmarks, confidence calibration analysis, cost-performance comparison vs v1/v2.