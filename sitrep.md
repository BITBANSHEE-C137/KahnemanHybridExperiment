# v2 Training SITREP

## v2 Training Status
**Step 33,200/50,000 (66.4% complete)** | A10G @ 100% util, 194W/300W | **4.85 steps/min** | ETA: **58 hours** | Current spot: **$0.45/hr** (62.7% savings) | Session cost: **$2.91**, total: **$21.93**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 26000 | 31.46  | 4.06      | 28.0%   | 0.863 | 0.018 |
| 28000 | 31.32  | 3.95      | 28.2%   | **0.872** | 0.007 |
| 30000 | 31.68  | 4.08      | 28.1%   | 0.864 | 0.023 |
| 32000 | 31.39  | 3.96      | 28.4%   | **0.871** | 0.013 |
| 33000 | **31.29** | 4.23    | 25.4%   | 0.864 | **0.008** |

**AR PPL improving steadily** (-0.17 since 26k). **S1 accuracy volatile** (25.4% vs 28.4% prev). **ECE excellent** at 0.008. AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **31.29** | ✅ **MET** |
| AUROC  | > 0.75 | **0.864** | ✅ **MET** |
| ECE    | < 0.05 | **0.008** | ✅ **MET** |
| Diff Loss | → 4.0 | 4.23    | 🔶 Close |
| S1 Acc | → 40%  | 25.4%   | ❌ **MISS** |

**3/5 targets met**. S1 accuracy **15pp below target**, trending down.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. **v2 AR significantly better** (31.29 vs 43.86 PPL). **S1 performance concerning** - accuracy should be ~40% by now based on v1's final loss.

## Infrastructure  
**13 sessions, 12 spot reclaims** over 2.5 days. Current session: **6.4h uptime** in us-east-1b. **Stable run** - longest session was 10h. Total **62.7% cost savings** vs on-demand. No infrastructure issues.

## What's Next
At current rate: **completion by March 8 16:00 UTC**. Priority: **diagnose S1 accuracy regression** - may need hyperparameter adjustment or architectural review. Post-completion: v2 benchmarks, confidence calibration analysis, v1 vs v2 head-to-head comparison on LAMBADA/WikiText.