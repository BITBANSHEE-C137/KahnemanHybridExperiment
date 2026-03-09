# v3 Training SITREP

## v3 Training Status
**Step 12,800/50,000 (25.6% complete)** | A10G @ 100% util, 197W/300W, 52°C | VRAM: 16.2/23.0GB | **Rate: ~400 steps/hr** | ETA: ~4 days | **Spot cost: $0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 5000 | 24.35  | 0.695 | 0.008 | 6.12 | 9.1% |
| 8000 | 26.29  | 0.785 | 0.008 | 5.60 | 12.6% |
| 10000| 27.55  | 0.828 | 0.005 | 4.98 | 19.0% |
| **12000**| **28.12** | **0.853** | **0.007** | **4.31** | **25.0%** |

**Trends**: AR PPL **regressing** (+15% since step 5k). AUROC **improving** strongly (+23%). Diffusion loss **converging well** (-30%). S1 accuracy **accelerating** (+174%). ECE stable/excellent.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.12** | ✅ **MET** |
| AUROC > 0.75 | **0.853** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **4.31** | 🟡 **92% there** |
| S1 accuracy → 40% | **25.0%** | 🟡 **63% there** |

**3/5 targets met**. Diff loss and S1 acc trending correctly but need more steps.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **Current v3 AR PPL (28.12) significantly better than v1 (43.86)**. S1 performance gap remains large but closing rapidly.

## Infrastructure
**Current session**: 15.7hr uptime, $7.17 spot cost. **Previous session**: terminated after 6.8hr, $3.11 cost. **Total**: 2 spot reclaims, $10.25 total cost, 89% uptime. **Risk**: trending toward daily reclaims in us-east-1a.

## What's Next
Monitor AR PPL regression - **concerning divergence from joint training optimum**. S1 acceleration promising for 40% target by step 20k. Consider learning rate adjustment if AR degradation continues. Checkpoint sync running normally.