# SITREP: v2 Training Status
*2026-03-07 02:00 UTC*

## v2 Training Status
**Progress:** 47.7k/50k steps (95.4%) | **Rate:** ~400 steps/hour | **ETA:** ~6 hours  
**GPU:** A10G 100% util, 199W/300W, 51°C, 16.6/23GB VRAM  
**Spot Cost:** $0.46/hr (61.8% savings) | **Total:** $30.17 across 15 sessions

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 40k  | 30.21  | 4.56      | 23.2%   | 0.857 | 0.007 |
| 41k  | 30.12  | 4.47      | 25.1%   | 0.862 | 0.012 |
| 42k  | 30.08  | 4.07      | 29.0%   | 0.862 | 0.016 |
| 43k  | 29.96  | 3.93      | 29.2%   | 0.868 | 0.020 |
| 44k  | 29.96  | 4.37      | 25.4%   | 0.865 | 0.016 |
| 45k  | 29.80  | 3.86      | 29.3%   | **0.875** | 0.016 |
| 46k  | 29.74  | 4.15      | 26.2%   | 0.865 | 0.011 |
| 47k  | **29.72** | **4.61** | **22.7%** | **0.855** | **0.011** |

**🔴 REGRESSION ALERT:** S1 accuracy dropped from 29.3% to 22.7% (step 45k→47k). AUROC declined 0.875→0.855. Diffusion loss spiked to 4.61.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.72** | ✅ |
| AUROC | > 0.75 | **0.855** | ✅ |
| ECE | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.61** | 🔴 |
| S1 Accuracy | → 40% | **22.7%** | 🔴 |

**3/5 targets met.** Diffusion and S1 performance regressing in final phase.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%/29.07 PPL  
v2 current AR PPL (**29.72**) significantly better than v1 (43.86), approaching GPT-2 baseline.

## Infrastructure
**Current:** 8.3h uptime, no interruptions  
**History:** 15 spot sessions, 14 reclaims (heavy churn days 4-5)  
**Stability:** Improved since moving to us-east-1b yesterday

## What's Next
Training completes in ~6 hours. Critical: analyze S1/diffusion regression in final 2k steps. Post-completion: benchmark suite, v1 vs v2 comparison, confidence calibration deep-dive.