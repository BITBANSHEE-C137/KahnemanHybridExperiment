# v3 Training SITREP - 2026-03-11 09:00 UTC

## v3 Training Status
**Step 40,800/50,000** (81.6% complete) • **L4 GPU 100% utilized** @ 72W/81°C • Current rate: ~5.9 steps/min • **ETA: ~26 hours** • Spot rate: **$0.43/hr** (56.5% savings) • Session cost: **$0.70**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 33000 | 28.93 | 4.09 | 26.6% | 0.861 | 0.009 |
| 34000 | 28.85 | 4.15 | 25.6% | 0.871 | 0.007 |
| 35000 | 28.73 | 4.26 | 25.0% | 0.863 | 0.006 |
| 36000 | 28.59 | 4.46 | 23.5% | 0.864 | 0.011 |
| 37000 | 28.51 | 4.52 | 24.1% | 0.856 | 0.006 |
| 38000 | 28.43 | **4.02** | **28.5%** | 0.864 | 0.009 |
| 39000 | 28.34 | 4.04 | **29.0%** | 0.863 | 0.011 |
| 40000 | 28.27 | **3.76** | **30.3%** | **0.881** | 0.009 |

**Trends:** AR PPL steadily improving (-2.3%). **Diff loss volatile but trending down** (recent drop to 3.76). **S1 accuracy recovering** (+6.8% from step 36k). AUROC stable ~0.86, **spiked to 0.881** at 40k.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **28.3** | ✅ **MET** |
| AUROC | > 0.75 | **0.881** | ✅ **MET** |
| ECE | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **3.76** | ✅ **EXCEEDED** |
| S1 Accuracy | → 40% | **30.3%** | ❌ **24% to target** |

**4/5 targets met.** S1 accuracy trending positively but needs **+9.7pp** improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. 
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07.

**Current v3 AR performance (28.3 PPL) approaching GPT-2 baseline quality.** S1 accuracy (30.3%) significantly improved from v1's implied ~18% baseline.

## Infrastructure
**21 spot sessions, 7 instance types** • Multiple reclaims 3/9-3/10 (11 brief interruptions) • **Stable 1.6h current session** • Total cost: **$33.02** vs $49.92 on-demand • Current L4 instance performing well, no thermal issues

## What's Next
**9,200 steps remaining** (~26hrs) • Monitor S1 accuracy trajectory toward 40% target • Post-completion: comprehensive v2 benchmarks, confidence calibration analysis, v1/v2/v3 comparative evaluation