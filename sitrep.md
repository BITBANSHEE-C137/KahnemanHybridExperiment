## v4 Training Status
**56% complete** (42k/75k steps). A10G @ **100% util**, 204W/300W, 56°C. **13.0 hrs uptime**, **0.3 steps/sec** rate. ETA: **25.6 hrs** remaining. Current spot: **$0.44/hr** (64% savings vs $1.21 on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 38500 | 29.30 | 4.276 | 28.0% | 0.858 | 0.012 |
| 39000 | 29.17 | 4.082 | 30.5% | 0.857 | 0.008 |
| 40000 | 29.05 | 3.791 | 32.7% | 0.862 | 0.018 |
| 41000 | 28.84 | 3.937 | 30.9% | 0.864 | 0.016 |
| **42000** | **28.80** | **4.024** | **30.2%** | **0.861** | **0.006** |

**Strong AR perplexity improvement** (-0.5 over 3.5k steps). Diffusion loss **regressed** from 3.79 → 4.02. S1 accuracy **volatile** but trending down from 32.7% peak. **ECE excellent** at 0.006.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.8** | ✅ **PASS** |
| AUROC > 0.75 | **0.861** | ✅ **PASS** |
| ECE < 0.05 | **0.006** | ✅ **PASS** |
| Diff Loss → 4.0 | **4.024** | ⚠️ **MARGINAL** |
| S1 Acc → 40% | **30.2%** | ❌ **FAIL** (-9.8pp) |

**3/5 targets met**. S1 accuracy significantly behind target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

**Current v4 AR performance superior** to both v1 (28.8 vs 43.86 PPL). S1 performance comparable to v1 baseline.

## Infrastructure
**73 spot sessions**, current instance stable for **13.0 hrs** (longest recent run). Total cost **$54.14** vs $88.38 on-demand projection. **Frequent early reclaims** in Mar 19-21 period causing training instability. Recent stability improvement suggests better spot pricing/availability.

## What's Next
Target **step 45k checkpoint** for mid-training eval. **S1 accuracy plateau** concerning - may need learning rate adjustment or longer convergence. Diffusion loss regression needs monitoring. Strong AR performance suggests core dual-process architecture working.