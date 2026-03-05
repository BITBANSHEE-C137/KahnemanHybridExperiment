# v2 Training SITREP

## v2 Training Status
**Step 20,500/50,000 (41.0%)** | GPU: **100% util**, A10G @ 52°C, 16.6/23GB VRAM | Rate: **~2.45 steps/min** | ETA: **~8.3 days** | Spot: **$0.44/hr** (63.9% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 13000| 30.50  | 4.40      | 25.5%   | 0.852 | 0.012 |
| 16000| 30.79  | 4.13      | 26.8%   | 0.860 | 0.007 |
| 18000| 30.77  | 4.03      | 27.2%   | 0.869 | 0.006 |
| 20000| **30.92** | **4.75** | **21.3%** | **0.851** | **0.007** |

**🚩 REGRESSIONS**: S1 accuracy **crashed 6% since step 18k**. Diffusion loss **spiked +0.7**. AUROC **degraded -0.018**. AR PPL stable but trending up.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.92** | ✅ **MET** |
| AUROC > 0.75 | **0.851** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **4.75** | ❌ **+19% over** |
| S1 accuracy → 40% | **21.3%** | ❌ **47% under** |

**2/5 targets missed**. S1 performance concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.92) already outperforming v1 WikiText baseline**.

## Infrastructure
**10 spot sessions**, **9 reclaims** in 36 hours. Current instance: 8.3hr uptime, us-east-1f. Total cost: **$13.55** ($3.58 current session). **Extremely unstable** - averaging 3.6hr per instance before termination.

## What's Next
**IMMEDIATE**: Investigate S1 accuracy collapse - possible confidence head divergence or learning rate issue. **After v2**: Full benchmark suite, v1 vs v2 head-to-head, confidence calibration deep-dive.