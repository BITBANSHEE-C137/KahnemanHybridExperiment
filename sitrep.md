# v3 Training Status SITREP

## v3 Training Status
**Step 32,200/50,000** (64.4% complete) | L4 GPU @ **100% util**, 82°C, 72W | **14.1 hr ETA** | Spot rate **$0.46/hr** (53% savings) | Current session cost **$6.45**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 25000 | 29.48 | 4.08 | 26.5% | 0.861 | 0.004 |
| 26000 | 29.58 | 4.02 | 27.7% | 0.864 | 0.006 |
| 27000 | 29.55 | 4.32 | 24.6% | 0.866 | 0.011 |
| 28000 | 29.40 | 4.51 | 23.8% | 0.865 | 0.007 |
| 29000 | 29.36 | 4.27 | 25.5% | 0.867 | 0.012 |
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.005 |
| 31000 | 28.95 | 4.47 | 23.3% | 0.871 | 0.003 |
| 32000 | **29.04** | **4.35** | **24.2%** | **0.865** | **0.009** |

**Trends**: AR PPL slowly improving (↓0.4 over 7k steps). S1 accuracy **regressing** (-3.5% from peak). Confidence calibration excellent (ECE < 0.012). AUROC plateaued ~0.866.

## Target Scorecard
| Target | Current | Status |
|---------|---------|---------|
| AR PPL < 40 | **29.04** | ✅ **PASS** |
| AUROC > 0.75 | **0.865** | ✅ **PASS** |
| ECE < 0.05 | **0.009** | ✅ **PASS** |
| Diff loss → 4.0 | **4.35** | ❌ Not converging |
| S1 accuracy → 40% | **24.2%** | ❌ **Far from target** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12. **Current v3 AR PPL 34% better than v1** (29.04 vs 43.86), but diffusion loss **stalled above target**. S1 token accuracy needs **+16pp improvement**.

## Infrastructure
**19 spot sessions**, total cost **$26.44**. Current g6.2xlarge session: **14.1h uptime**, stable. **Heavy spot churn** in first 2 days (11 reclaims between steps 19k-21k), now stable on current instance since step 24.9k. Checkpoints syncing normally.

## What's Next
**Target completion**: ~14 hours. Monitor S1 accuracy regression - may need LR adjustment. Post-completion: comprehensive v1/v3 benchmarks, confidence head analysis, ablation on dual-process interference.