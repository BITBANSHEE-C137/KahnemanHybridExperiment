# ML Ops SITREP - v3 Training Status

## v3 Training Status
**Step 35,700/50,000** (71.4% complete) | GPU: **98%** util @ 81°C | Rate: ~1.4 steps/min | **ETA: ~7 days** | Current spot: **$0.46/hr** (53% savings) | Total cost: **$29.21**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 28000 | 29.40 | 4.51 | 23.8% | 0.865 | 0.0068 |
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.0046 |
| 32000 | 29.04 | 4.35 | 24.2% | 0.865 | 0.0089 |
| 34000 | 28.85 | 4.15 | 25.6% | 0.871 | 0.0069 |
| **35000** | **28.73** | **4.26** | **25.0%** | **0.863** | **0.0057** |

**Trends**: AR PPL steadily improving (-2.3% over 7k steps). Diff loss volatile but trending down. S1 accuracy stalled ~25%. AUROC stable but regressed slightly from 34k peak.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.73** | ✅ **BEAT** |
| AUROC > 0.75 | **0.863** | ✅ **BEAT** |
| ECE < 0.05 | **0.0057** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.26** | 🟡 **6.5% away** |
| S1 accuracy → 40% | **25.0%** | ❌ **37.5% gap** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v3 AR PPL (28.73) already beating v1 WikiText performance**. S1 accuracy severely lagging - needs investigation.

## Infrastructure
**19 spot sessions**, **20+ interruptions** since step 19k. Current g6.2xlarge stable for **20h** (longest recent session). Cost efficiency: **53% savings** vs on-demand. Multiple failed starts around step 20k suggest AZ capacity issues in us-east-1b.

## What's Next
**Critical**: S1 accuracy plateau at 25% vs 40% target. Consider learning rate adjustment or architecture review. Diff loss close to target - should hit 4.0 by completion. After v3: comprehensive v1/v2/v3 benchmark comparison, confidence calibration analysis.