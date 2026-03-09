# v3 Training SITREP

## v3 Training Status
**Step 15,300/50,000** (30.6% complete). A10G at **100% util**, 198W/300W, 49°C, 16.2GB/23GB VRAM. Rate: ~400 steps/day. **ETA: 87 days**. Current spot cost: **$0.45/hr** (62% savings vs on-demand $1.21/hr).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 8000 | 26.29 | 5.60 | 12.6% | 0.785 | 0.0076 |
| 10000 | 27.55 | 4.98 | 19.0% | 0.828 | 0.0053 |
| 12000 | 28.12 | 4.31 | 25.0% | 0.853 | 0.0066 |
| 14000 | 28.51 | 4.29 | 24.7% | 0.852 | 0.0087 |
| 15000 | **28.64** | **4.50** | **23.7%** | **0.864** | **0.0052** |

**🔴 Regression alert**: Diffusion loss increased from 4.29→4.50, S1 accuracy dropped 24.7%→23.7%. AR PPL continues slow degradation trend.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.64** | ✅ |
| AUROC | > 0.75 | **0.864** | ✅ |
| ECE | < 0.05 | **0.0052** | ✅ |
| Diff Loss | → 4.0 | **4.50** | ❌ (+0.5 from target) |
| S1 Accuracy | → 40% | **23.7%** | ❌ (-16.3pp from target) |

**3/5 targets met**. S1 performance plateau concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. Current v3 AR PPL (**28.64**) significantly better than v1 baseline (**43.86**).

## Infrastructure  
**Total cost: $11.61** across 2 spot sessions. Current instance: 18.6h uptime, 1 reclaim event (session 1→2). Stable spot pricing at $0.45/hr. Checkpoints syncing normally.

## What's Next
**Critical**: Investigate diff loss regression and S1 accuracy plateau. Consider learning rate adjustment or loss weighting rebalance. Monitor for further degradation over next 5K steps before intervention.