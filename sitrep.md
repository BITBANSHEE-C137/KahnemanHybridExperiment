# v3 Training SITREP

## v3 Training Status
**Step 42,300/50,000 (84.6% complete)** | GPU: 100% util, 70W/72W, 79°C | L4 VRAM: 16.6GB/23GB | Rate: ~300 steps/hr | **ETA: ~26 hours** | Spot cost: **$0.43/hr** (56.5% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 35000 | 28.73 | 4.26 | 24.97% | 0.863 | 0.006 |
| 36000 | 28.59 | 4.46 | 23.45% | 0.864 | 0.011 |
| 37000 | 28.51 | 4.52 | 24.13% | 0.856 | 0.006 |
| 38000 | 28.43 | 4.02 | **28.53%** | 0.864 | 0.009 |
| 39000 | 28.34 | 4.04 | 29.04% | 0.863 | 0.011 |
| 40000 | 28.27 | **3.76** | **30.28%** | **0.881** | 0.009 |
| 41000 | 28.30 | 3.95 | 27.81% | 0.866 | 0.011 |
| **42000** | **28.33** | **3.89** | **29.15%** | **0.870** | **0.013** |

**Trends:** AR PPL plateaued ~28.3. Diffusion loss trending down from 4.26→3.89. S1 accuracy volatile but generally improving. AUROC peaked at 40k (0.881), slight regression since. ECE stable <0.015.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.33** | ✅ **Met** |
| AUROC > 0.75 | **0.870** | ✅ **Met** |
| ECE < 0.05 | **0.013** | ✅ **Met** |
| Diff loss → 4.0 | **3.89** | ✅ **Met** |
| S1 accuracy → 40% | **29.15%** | ❌ **73% to target** |

**4/5 targets met.** S1 accuracy needs +11pp to reach 40%.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **Current v3 AR performance (28.33 PPL) already superior to v1 WikiText (43.86)**. Diffusion loss 3.89 vs v1's 4.12 shows continued S1 improvement.

## Infrastructure
**21 spot sessions, $34.12 total cost.** Current g6.2xlarge stable 4.1hr uptime. Previous session volatility (9-10 March): 17 reclaims in 2 days due to aggressive spot bidding. Switched to g6.2xlarge in us-east-1b - **more stable, 57% savings maintained**.

## What's Next
**7,700 steps remaining (~26hr).** Upon v3 completion: comprehensive v1/v2/v3 benchmarking on LAMBADA/WikiText, confidence calibration analysis, S1 token prediction quality assessment. Priority: determine if S1 accuracy plateau breaks through 40% threshold.