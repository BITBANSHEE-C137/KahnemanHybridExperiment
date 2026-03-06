# v2 Training Status SITREP

## v2 Training Status
**Step 33.6k/50k (67.2%)** | GPU: **99% util**, A10G @ 53°C, 16.6/23GB VRAM | Rate: ~6.5 steps/min | ETA: **41.7hrs** | Spot: **$0.45/hr** (63% savings)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 26k  | 31.46  | 4.06     | 28.0%  | 0.863 | 0.018 |
| 28k  | 31.32  | 3.95     | 28.2%  | **0.872** | 0.007 |
| 30k  | 31.68  | 4.08     | 28.1%  | 0.864 | 0.023 |
| 32k  | 31.39  | 3.96     | 28.4%  | 0.871 | 0.013 |
| 33k  | **31.29** | 4.23   | 25.4%  | 0.864 | **0.008** |

**Trends:** AR PPL stable around 31.3, **S1 accuracy dropped 3%** at latest eval (concerning). AUROC steady ~0.86. ECE excellent at 0.008.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.29** | ✅ **PASS** |
| AUROC > 0.75 | **0.864** | ✅ **PASS** |
| ECE < 0.05 | **0.008** | ✅ **PASS** |
| Diff loss → 4.0 | **4.23** | ❌ Above target |
| S1 accuracy → 40% | **25.4%** | ❌ **15% gap** |

**3/5 targets met.** S1 accuracy regressing, diff loss volatile.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
v2 AR PPL (**31.29**) significantly better than v1 WikiText (43.86). S1 performance unclear without loss conversion.

## Infrastructure
**13 sessions, 12 spot reclaims** over 2.5 days. Current instance stable **6.9hrs**. Total cost **$22.11** vs $32.49 on-demand. Most reclaims in us-east-1b/1f zones. **Persistent spot volatility** impacting training rhythm.

## What's Next
**16.4k steps remaining** (~42hrs). Monitor S1 accuracy regression closely. After completion: comprehensive v1/v2 benchmarks on LAMBADA/WikiText, confidence calibration analysis, final cost efficiency report.