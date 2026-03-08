# v3 Training SITREP - 2026-03-08 15:00 UTC

## v3 Training Status
**Step 800/50k (1.6%)** | A10G @ **100% util** (205W, 58°C) | VRAM: 16.2/23GB  
Rate: ~137 steps/hour | **ETA: ~15 days** | Spot: **$0.46/hr** (62% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 4.98%  | 0.555 | 0.004 |

⚠️ **Only one eval point available** - trend analysis pending more data

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **21.29** | ✅ **MET** |
| AUROC | > 0.75 | **0.555** | ❌ Need +0.20 |
| ECE | < 0.05 | **0.004** | ✅ **MET** |
| Diff Loss | → 4.0 | **6.75** | ❌ Need -2.75 |
| S1 Accuracy | → 40% | **4.98%** | ❌ Need +35% |

**2/5 targets met** - AR performance already strong, confidence/S1 lagging

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
Current v3 AR PPL (21.29) **outperforming** v1 WikiText baseline early in training

## Infrastructure
**Current session**: 1.16h uptime, $0.53 cost  
**Previous session**: 6.77h, completed steps 400→1000, $3.11  
**Total cost**: $3.61 across 2 sessions | **No spot reclaims** - stable training

## What's Next
- Monitor AUROC/S1 accuracy improvement over next 5k steps
- First comprehensive eval suite at step 5000
- **Critical**: Confidence head not learning (0.0 accuracy) - investigate head initialization