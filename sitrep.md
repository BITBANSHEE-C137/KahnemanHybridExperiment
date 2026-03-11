# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 37,800/50,000 (75.6%)** | GPU: **100%** util on L4 @ 81°C | Rate: ~300 steps/hr | ETA: **41 hrs** | Current spot: **$0.46/hr** (53% savings) | Projected total: **$20.41**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.005 |
| 33000 | 28.93 | 4.09 | **26.6%** | 0.861 | 0.009 |
| 35000 | 28.73 | 4.26 | 25.0% | 0.863 | 0.006 |
| **37000** | **28.51** | **4.52** | **24.1%** | **0.856** | **0.006** |

**Trends:** AR PPL improving steadily (**-2.3%** since 30k). Diff loss **degrading** (+4.1%). S1 accuracy **stalled** around 24%. AUROC **declining** (-1.4%).

## Target Scorecard
- ✅ **AR PPL < 40**: 28.51 (PASS)
- ✅ **AUROC > 0.75**: 0.856 (PASS)  
- ✅ **ECE < 0.05**: 0.006 (PASS)
- ❌ **Diff loss → 4.0**: 4.52 (FAIL - trending worse)
- ❌ **S1 accuracy → 40%**: 24.1% (FAIL - far from target)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current AR PPL (28.51) already beating WikiText baseline**, suggesting strong performance trajectory.

## Infrastructure
**19 spot sessions** | Total cost: **$30.83** | Current g6.2xlarge stable **23.6hrs** (longest run) | Previous sessions: frequent reclaims on 3/9 (14 interruptions in 6hrs) | **Stable since 3/10** - no recent spot issues.

## What's Next
**Critical:** Diffusion loss regression needs investigation. S1 accuracy plateau concerning - may need architecture/hyperparameter review. After completion: comprehensive v2 benchmarks, confidence calibration deep-dive, and v1 vs v2 head-to-head comparison.