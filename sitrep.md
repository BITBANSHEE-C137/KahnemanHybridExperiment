# v2 Training SITREP

## v2 Training Status
**Step 16800/50000 (33.6%)** | GPU: 100% util, 204W/300W, 52°C | Rate: ~400 steps/hr | **ETA: 3.5 days** | Spot: $0.44/hr (**63.9% savings**) | Total cost: **$11.62**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 9000 | 28.06 | 5.016 | 18.9% | 0.843 | 0.0057 |
| 10000 | 28.39 | 4.372 | 25.1% | 0.850 | 0.0044 |
| 11000 | 28.91 | 4.186 | 26.0% | 0.857 | 0.0046 |
| 12000 | 29.35 | 4.342 | 25.6% | 0.852 | 0.0093 |
| 13000 | 30.50 | 4.402 | 25.5% | 0.852 | 0.0124 |
| 14000 | 30.34 | 4.307 | 26.0% | 0.853 | 0.0111 |
| 15000 | 31.05 | 4.328 | 26.1% | 0.852 | 0.0139 |
| **16000** | **30.79** | **4.128** | **26.8%** | **0.860** | **0.0071** |

**Trends:** AR PPL degrading (+9.7% since step 9k). Diff loss improving but volatile. S1 accuracy stalled at ~26%. **AUROC recovering** (+0.017 recent). ECE unstable but recent improvement.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.79** | ✅ |
| AUROC | > 0.75 | **0.860** | ✅ |
| ECE | < 0.05 | **0.0071** | ✅ |
| Diff Loss | → 4.0 | **4.128** | 🔶 Close |
| S1 Accuracy | → 40% | **26.8%** | ❌ Behind |

**3/5 targets met.** S1 accuracy plateau is concerning—may need LR adjustment.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26% acc, 1.46 PPL | WikiText-103 43.86 PPL | S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08% acc, WikiText 29.07 PPL
**Current v2 AR performance tracking ahead of v1 baseline.**

## Infrastructure
**10 spot sessions, 7 reclaims** | Current: us-east-1f, 3.8h uptime | Recent stability good | g5.2xlarge performing well at 72% VRAM utilization | Checkpoints syncing properly

## What's Next
- Monitor S1 accuracy plateau—consider LR schedule adjustment at step 20k
- Diff loss needs 3% improvement to hit target
- Full benchmarks at step 25k, 35k, 50k
- v1 vs v2 head-to-head analysis on completion