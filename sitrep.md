## v4 Training Status
**Step 39k/75k (52%)** | GPU: **98% util** A10G @ 57°C | Rate: ~5.4 steps/min | **ETA: 7d** | Current spot: **$0.44/hr** (64% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 35500 | 31.11 | 4.40 | 28.1% | 0.857 | 0.038 |
| 36000 | 31.11 | 4.20 | 29.9% | 0.864 | 0.021 |
| 37000 | 30.10 | 4.34 | 27.7% | 0.854 | 0.020 |
| 38000 | 29.43 | 4.38 | 27.7% | 0.856 | 0.016 |
| **39000** | **29.17** | **4.08** | **30.5%** | **0.857** | **0.008** |

**Trends:** AR PPL steadily improving (**-6%** in 3.5k steps). ECE excellent improvement (**-79%**). S1 accuracy volatile but trending up. AUROC stable ~0.857.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.17** | ✅ **-27%** |
| AUROC > 0.75 | **0.857** | ✅ **+14%** |
| ECE < 0.05 | **0.008** | ✅ **-84%** |
| Diff loss → 4.0 | **4.08** | 🟡 **2% away** |
| S1 accuracy → 40% | **30.5%** | 🔴 **24% short** |

**3/5 targets met.** Diffusion loss nearly there, S1 accuracy lagging.

## v1 Benchmark Baseline
v1 final LAMBADA: 94.26%, PPL: 1.46 | WikiText PPL: 43.86 | S1 loss: 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL: 29.07

**Current AR performance already beats v1 WikiText** (29.17 vs 43.86). On track to match GPT-2 baseline.

## Infrastructure
**73 spot sessions** since March 18. Current: 7.5h uptime on g5.2xlarge. **Total cost: $51.72** (64% savings vs on-demand $88.35).

**Spot reliability poor:** 15+ interruptions in 24h window (Mar 19-20). Stabilized since Mar 21 with longer sessions. Current instance stable 7.5h.

## What's Next
**36k more steps** (~7 days). Priority: **S1 accuracy breakthrough** - only metric significantly behind. Consider confidence head analysis if AUROC plateaus. Benchmark run due at step 50k for v1 comparison.