# v2 Training SITREP

## v2 Training Status
**Step 49,400/50,000 (98.8%)** | GPU: **98% util** A10G @ 50°C | Rate: ~500 steps/hr | **ETA: 72 min** | Spot: **$0.46/hr** (61.8% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 42000| 30.08  | 4.07      | 29.0%  | 0.862 | 0.016 |
| 45000| 29.80  | 3.86      | 29.3%  | 0.875 | 0.016 |
| 47000| 29.72  | 4.61      | 22.7%  | 0.855 | 0.011 |
| 48000| 29.72  | 4.73      | 21.9%  | 0.858 | 0.012 |
| **49000**| **29.64** | **4.24** | **25.4%** | **0.865** | **0.010** |

**Trends:** AR PPL improving slowly. **S1 accuracy volatile** - dropped 7% then recovered 4%. Diffusion loss spiked at 47k-48k, now stabilizing. AUROC recovering from 47k dip.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.64** | ✅ **Met** |
| AUROC > 0.75 | **0.865** | ✅ **Met** |
| ECE < 0.05 | **0.010** | ✅ **Met** |
| Diff loss → 4.0 | **4.24** | 🟡 Close |
| S1 accuracy → 40% | **25.4%** | ❌ **15% short** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL
**v2 AR substantially better than v1** (29.64 vs 43.86 PPL). S1 training still underperforming.

## Infrastructure
Current session: **10.3hr uptime**, $4.77 cost | **15 total sessions** | **14 spot reclaims** (high churn) | Total: **$31.10** over 3 days | Last checkpoint: step_49000.pt (1.5GB, synced)

## What's Next
**600 steps to completion** → Full v2 benchmarks on LAMBADA/WikiText → **Detailed v1 vs v2 comparison** → S1 token accuracy deep-dive (why 15% below target?) → Confidence calibration analysis