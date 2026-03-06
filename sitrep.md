# v2 Training SITREP

## v2 Training Status
**Progress:** 44k/50k steps (**88%** complete)  
**Rate:** ~3.3 steps/sec (13k steps in 3.6hrs)  
**GPU:** A10G @ 100% util, 65°C, 16.6/23GB VRAM  
**ETA:** ~30 mins to completion  
**Spot Cost:** $0.46/hr (62% savings), **$1.76** session cost

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 37k  | 30.65  | 4.75      | 0.216   | 0.861 | 0.007 |
| 38k  | 30.44  | **4.28**  | **0.267** | 0.865 | 0.004 |
| 39k  | 30.41  | **3.80**  | **0.307** | 0.863 | 0.007 |
| 40k  | 30.21  | 4.56      | 0.232   | 0.857 | 0.007 |
| 41k  | 30.12  | 4.47      | 0.251   | 0.862 | 0.012 |
| 42k  | 30.08  | **4.07**  | **0.290** | 0.862 | 0.016 |
| 43k  | **29.96** | **3.93** | **0.292** | **0.868** | **0.020** |
| 44k  | 29.96  | 4.37      | 0.254   | 0.865 | 0.016 |

**Trends:** AR PPL steadily improving. S1 accuracy volatile but trending up. **ECE degrading** - confidence calibration worsening. Diff loss erratic around target.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.96** | ✅ |
| AUROC | > 0.75 | **0.865** | ✅ |
| ECE | < 0.05 | **0.016** | ✅ |
| Diff Loss | → 4.0 | **4.37** | 🟡 Close |
| S1 Accuracy | → 40% | **25.4%** | ❌ Behind |

**3/5 targets met.** S1 accuracy significantly behind. Diff loss close but unstable.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 4.12 loss  
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v2 AR already outperforming v1 WikiText** (29.96 vs 43.86). Joint training working better than v1.

## Infrastructure  
**15 spot sessions**, **$28.05** total cost (vs $75.78 on-demand)  
Current session: 3.8hrs uptime, stable  
**Spot history:** Multiple reclaims early (4 in first day), stable 16hr session yesterday, current session running smoothly

## What's Next
6k steps remaining (~30min). Post-completion: full v2 benchmarks, head-to-head v1/v2 comparison, confidence calibration analysis (ECE regression concerning). **S1 underperformance needs investigation.**