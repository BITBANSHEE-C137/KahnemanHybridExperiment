# v2 Training SITREP

## v2 Training Status
**Step 28,100/50,000 (56.2% complete)**
- GPU: **99% utilization**, A10G running cool at 52°C, 16.6/23GB VRAM
- Rate: ~330 steps/hr | ETA: **66 hours** (March 8 evening)
- Spot cost: **$0.45/hr** (62.8% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 21000 | 30.88  | 4.85      | 0.207  | 0.851 | 0.0075 |
| 22000 | 30.95  | 4.19      | 0.275  | 0.858 | 0.0096 |
| 23000 | 31.03  | 4.03      | 0.279  | 0.864 | 0.0095 |
| 24000 | 30.98  | 4.46      | 0.243  | 0.863 | 0.0050 |
| 25000 | 31.22  | 4.20      | 0.276  | 0.860 | 0.0120 |
| 26000 | 31.46  | 4.06      | 0.280  | 0.863 | 0.0177 |
| 27000 | 31.46  | 4.48      | 0.244  | 0.862 | 0.0095 |
| **28000** | **31.32** | **3.95** | **0.282** | **0.872** | **0.0073** |

**Trends:** AR PPL stable ~31. **Diff loss trending down** (4.85→3.95). S1 accuracy volatile but improving. **AUROC steadily climbing** to 0.872. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.32** | ✅ **MET** |
| AUROC > 0.75 | **0.872** | ✅ **MET** |
| ECE < 0.05 | **0.0073** | ✅ **MET** |
| Diff loss → 4.0 | **3.95** | ✅ **APPROACHING** |
| S1 accuracy → 40% | **28.2%** | ❌ **Gap: 11.8%** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL
v2 current AR performance similar to v1, **diff loss beating v1 target**.

## Infrastructure
**12 spot reclaims** over 2.5 days, total cost **$18.75** (vs $38 on-demand)
Current session: 5.1hrs uptime, us-east-1a stable
**62.8% cost savings** maintaining, no recent interruptions

## What's Next
**22k steps remaining** (~66hrs). Expecting S1 accuracy breakthrough above 30%. Post-completion: full benchmark suite, confidence calibration analysis, v1/v2 head-to-head comparison.