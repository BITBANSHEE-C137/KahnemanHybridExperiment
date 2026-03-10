# v3 Training SITREP

## v3 Training Status
**Step 27,500/50,000** (55% complete) | GPU: **100% util** @ 82°C | Rate: ~1.3 steps/sec | ETA: **14.2 hours** | Spot: **$0.46/hr** (53% savings)

Current L4 instance stable 6.1h, **$2.78** session cost.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 20000| 29.22  | 4.24      | 26.8%  | 0.857 | 0.005|
| 22000| 29.70  | **3.95**  | **28.3%** | **0.876** | 0.004|
| 25000| 29.48  | 4.08      | 26.5%  | 0.861 | 0.004|
| 27000| **29.55** | 4.32   | 24.6%  | 0.866 | **0.011**|

**Trends:** AR PPL plateaued ~29.5. S1 accuracy **regressed** from 28.3% peak. ECE **deteriorating** (0.004→0.011). AUROC stable ~0.866.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40.0 | **29.55** | ✅ **MET** |
| AUROC  | > 0.75 | **0.866** | ✅ **MET** |
| ECE    | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.32** | ⚠️ **CLOSE** |
| S1 Acc | → 40% | **24.6%** | ❌ **MISS** |

## v1 Benchmark Baseline
v1@50k: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 AR performance approaching GPT-2 baseline.** S1 accuracy significantly behind v1 pace.

## Infrastructure
**19 spot sessions**, **$22.77** total cost vs $43.26 on-demand. Multiple **reclaims** 3/9 evening (11 instances <1h). 

Current g6.2xlarge@us-east-1a **stable 6h+**. Last checkpoint: 1.5GB @ step 27000.

## What's Next
**22.5k steps remaining** (~14h). Monitor S1 accuracy regression - may need lr adjustment. ECE calibration degrading, investigate confidence head. Target completion **3/11 01:00 UTC**.

Post-completion: benchmark suite, v1→v3 progression analysis, confidence calibration deep-dive.