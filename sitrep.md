# v2 Training SITREP

## v2 Training Status
**Step 17,200/50,000 (34.4%)** | A10G @ **98% util** | **195W/300W** | **52°C** | Rate: ~4 steps/min | **ETA: ~90h** | Current spot: **$0.44/hr** (64% savings) | Session uptime: **4.3h**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 10000 | 28.39 | 4.37 | 25.1% | 0.850 | 0.004 |
| 12000 | 29.35 | 4.34 | 25.6% | 0.852 | 0.009 |
| 14000 | 30.34 | 4.31 | 26.0% | 0.853 | 0.011 |
| 16000 | 30.79 | 4.13 | 26.8% | 0.860 | 0.007 |
| **17000** | **30.70** | **4.52** | **23.7%** | **0.860** | **0.007** |

**Trends**: AR PPL plateaued ~30. Diff loss **volatile** (4.13→4.52). S1 accuracy **regressed** -3.1pp. AUROC improving (+0.01). ECE stable/good.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **30.7** | ✅ **MET** |
| AUROC > 0.75 | **0.860** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **4.52** | ❌ 0.52 above |
| S1 accuracy → 40% | **23.7%** | ❌ 16.3pp below |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (30.7) already better than v1 (43.86)**.

## Infrastructure
**10 spot sessions** | Total cost: **$11.80** (vs $53.29 on-demand) | **8 reclaims** in 36h | Current session stable 4.3h | Checkpoints: step_15000/16000/17000.pt | Sync running ✅

**Issue**: High reclaim rate impacting training efficiency.

## What's Next
Monitor S1 accuracy regression. Diff loss needs stabilization. After v2: benchmark comparison, confidence head analysis vs v1, investigate S1/AR interference.