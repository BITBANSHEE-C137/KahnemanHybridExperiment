# v3 Training SITREP

## v3 Training Status
**Step 19,900/50,000** (39.8% complete) | **97% GPU util** A10G @ 188W/300W, 53°C | **500 steps in 1.1h** (~455 steps/hr) | **ETA ~67h** to completion | **Spot cost $0.48/hr** (61% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|-------------|------------|----------|
| 12000 | 28.12  | 4.31      | 25.0%       | 0.853      | 0.0066   |
| 13000 | 28.41  | 4.42      | 24.1%       | 0.844      | 0.0110   |
| 14000 | 28.51  | 4.29      | 24.7%       | 0.852      | 0.0087   |
| 15000 | 28.64  | 4.50      | 23.7%       | 0.864      | 0.0052   |
| 16000 | 28.66  | 4.38      | 23.5%       | 0.856      | 0.0104   |
| 17000 | 28.89  | 4.34      | 25.2%       | 0.858      | 0.0079   |
| 18000 | 28.99  | 4.44      | 23.0%       | 0.858      | 0.0098   |
| 19000 | 29.21  | 4.39      | 22.1%       | 0.866      | 0.0106   |

**Concerning trends**: AR PPL **degrading** (+1.1 since step 12k). S1 accuracy **declining** (-2.9pp). Diff loss stuck ~4.4. Confidence calibration **worsening** (ECE up 60%).

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.21** | ✅ **MET** |
| AUROC > 0.75 | **0.866** | ✅ **MET** |
| ECE < 0.05 | **0.0106** | ✅ **MET** |
| Diff loss -> 4.0 | **4.39** | ❌ **Missing by 0.39** |
| S1 accuracy -> 40% | **22.1%** | ❌ **Missing by 17.9pp** |

**3/5 targets met**. S1 accuracy **severely underperforming**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance tracking worse than v1** (29.21 vs expected ~28 based on v1 trajectory).

## Infrastructure
**5 sessions, 4 spot reclaims** in 3 days. Total cost **$14.93**. Current g5.2xlarge stable 1.1h (longest session was 23.5h). **Frequent interruptions impacting training stability** - consider reserved capacity or higher bid.

## What's Next
**Investigate S1 head regression** - accuracy dropping when should be climbing to 40%. Consider learning rate adjustment for confidence head. Eval checkpoint at 20k to confirm trends before continuing to 50k.