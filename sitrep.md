# ML Ops SITREP - v3 Training Status

## v3 Training Status
**Step 25,400/50,000** (50.8% complete). GPU: **100% util**, L4 running hot at 82°C, 72% VRAM used. Current rate ~300 steps/hr. **ETA: ~3.4 days**. Spot cost: **$0.46/hr** (53% savings vs on-demand), projected total **$20.28**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 18000| 28.99  | 4.439     | 22.97% | 0.858 | 0.0098|
| 20000| 29.22  | 4.235     | 26.76% | 0.857 | 0.0048|
| 22000| 29.70  | 3.945     | 28.34% | **0.876** | 0.0039|
| 24000| 29.53  | 4.309     | 25.16% | 0.862 | 0.0055|
| 25000| **29.48** | 4.079  | 26.50% | 0.861 | **0.0042**|

**Trends**: AR PPL stable ~29.5. Diff loss volatile (3.94→4.31). S1 accuracy peaked at 28.34% (step 22k), now 26.5%. AUROC best at 22k (0.876), regressed to 0.861. **ECE improving** (0.0042 is excellent).

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.48** | ✅ **MET** |
| AUROC > 0.75 | **0.861** | ✅ **MET** |
| ECE < 0.05 | **0.0042** | ✅ **MET** |
| Diff loss → 4.0 | **4.079** | ✅ **MET** |
| S1 accuracy → 40% | **26.5%** | ❌ **MISS** (14% gap) |

**3/5 targets met**. S1 accuracy stalled well below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR PPL (29.48) significantly better than v1 (43.86)** and approaching GPT-2 baseline.

## Infrastructure
**19 spot sessions**, chronic instability 3/9-3/10 with **17 spot reclaims** in 6 hours. Total cost **$21.17** across g5/g6 instances. Current g6.2xlarge stable 2.5hrs, longest session was 23.5hrs (steps 1000-19300). **Spot market highly volatile**.

## What's Next
Continue to 50k steps. **S1 accuracy needs investigation** - stuck at ~26% vs 40% target. Post-completion: v3 benchmarks, confidence calibration analysis, v1 vs v3 performance delta assessment.