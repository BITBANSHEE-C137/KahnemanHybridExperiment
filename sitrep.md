# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 400/50000 (0.8%)** - Training resumed after **13 spot reclaims** since step 20k. Current instance: g5.xlarge (A10G) at $0.45/hr spot rate (55% savings). **GPU idle** (0% util, 11W power) - trainer appears stalled. ETA: ~347 days at current 0 step/min rate. Total spend: **$16.08**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |
| 14000 | 28.51 | 4.29 | 24.7% | 0.852 | 0.009 |
| 15000 | 28.64 | 4.50 | 23.7% | **0.864** | **0.005** |
| 16000 | 28.66 | 4.38 | 23.5% | 0.856 | 0.010 |
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.008 |
| 18000 | 28.99 | 4.44 | 23.0% | 0.858 | 0.010 |
| 19000 | 29.21 | 4.39 | 22.1% | **0.866** | 0.011 |
| 20000 | 29.22 | **4.24** | **26.8%** | 0.857 | **0.005** |

**Trends**: AR PPL **degrading** (+0.8 over 7k steps), diffusion loss **improving** (-0.18), S1 accuracy volatile but trending up, AUROC strong >0.85, ECE excellent <0.011.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40 | **29.22** | ✅ **MET** |
| AUROC | >0.75 | **0.857** | ✅ **MET** |
| ECE | <0.05 | **0.005** | ✅ **MET** |
| Diff Loss | 4.0 | **4.24** | 🟡 **CLOSE** |
| S1 Accuracy | 40% | **26.8%** | ❌ **MISS** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. Current v3 AR PPL (**29.22**) matches GPT-2 baseline but **33% worse** than v1 (43.86). S1 loss improving toward v1 target.

## Infrastructure
**Critical instability**: 13 sessions, 12 spot reclaims in <2 days. Current g5.xlarge stable 6min. Previous sessions: mostly <1hr uptime, frequent task switching between g5/g6 instances across AZs. **Training effectively stalled** - only 300 steps since step 20k despite $0.67 spend.

## What's Next
**Immediate**: Debug trainer freeze - GPU idle suggests training loop crash. **Medium-term**: Instance type stability analysis, consider reserved capacity. **Long-term**: v2 completion blocked until infrastructure stabilized. Current trajectory suggests **6+ months** to completion at this rate.