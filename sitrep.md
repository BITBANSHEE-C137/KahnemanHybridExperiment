# v2 Training SITREP

## v2 Training Status
**Step 34,000/50,000 (68%)** | **3.8 steps/min** | ETA **7.0 hours**
GPU: **100% util**, 193W/300W, 53°C, 16.6GB/23GB VRAM
Spot: **$0.45/hr** (62.7% savings), current session **$3.36**, total **$22.38**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 27k  | 31.46  | 4.48      | 24.4%  | 0.862 | 0.0095 |
| 28k  | 31.32  | 3.95      | 28.2%  | **0.872** | 0.0073 |
| 29k  | 31.43  | 4.21      | 27.7%  | 0.860 | **0.0217** |
| 30k  | 31.68  | 4.08      | 28.1%  | 0.864 | **0.0234** |
| 31k  | 31.60  | 4.49      | 24.5%  | 0.862 | 0.0141 |
| 32k  | 31.39  | 3.96      | 28.4%  | **0.871** | 0.0129 |
| 33k  | 31.29  | 4.23      | 25.4%  | 0.864 | 0.0075 |
| **34k** | **31.13** | **4.68** | **22.0%** | **0.854** | **0.0086** |

**Trends:** AR PPL slowly improving. **S1 accuracy regressing** (-6.4% from peak). AUROC volatile but trending down. ECE stable. **Diff loss stalled** around 4.0-4.7.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.13** | ✅ **MET** |
| AUROC > 0.75 | **0.854** | ✅ **MET** |
| ECE < 0.05 | **0.0086** | ✅ **MET** |
| Diff loss → 4.0 | **4.68** | ❌ **MISS** (+17%) |
| S1 accuracy → 40% | **22.0%** | ❌ **MISS** (-45%) |

**2/5 targets failing.** S1 accuracy notably worse than target.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26% / 1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current v2 AR PPL (31.13) already better than v1 WikiText (43.86)**

## Infrastructure
**13 spot sessions**, **$22.38 total cost** vs $45.86 on-demand
Current: 7.4h uptime, no reclaims since 01:33 UTC
**Spot stability good** - longest session 10h, avg 3.5h

## What's Next
**16k steps remaining** (~7 hours). **S1 accuracy decline concerning** - may need learning rate adjustment or longer training. After completion: benchmark suite, confidence calibration analysis, v1/v2 head-to-head comparison.