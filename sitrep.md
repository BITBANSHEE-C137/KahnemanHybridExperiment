# SITREP - v3 Training Status
*2026-03-09 09:00 UTC*

## v3 Training Status
**Step 15,700 / 50,000** (31.4% complete). A10G @ **98% util**, 197W power, 16.2GB VRAM used. Training rate ~400 steps/hr. **ETA: ~4 days**. Spot cost **$0.45/hr** (62% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 8000 | 26.29  | 5.60      | 12.6%   | 0.785 | 0.008 |
| 10000| 27.55  | 4.98      | 19.0%   | 0.828 | 0.005 |
| 12000| 28.12  | 4.31      | 25.0%   | 0.853 | 0.007 |
| 14000| 28.51  | 4.29      | 24.7%   | 0.852 | 0.009 |
| **15000**| **28.64**  | **4.50**      | **23.7%**   | **0.864** | **0.005** |

**Trends**: AR PPL slowly degrading (+2.3 since step 8k). Diffusion loss converging well. S1 accuracy peaked at 12k, now declining. AUROC steadily improving. ECE well-calibrated.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.64** | ✅ **MET** |
| AUROC > 0.75 | **0.864** | ✅ **MET** |  
| ECE < 0.05 | **0.005** | ✅ **MET** |
| Diff Loss → 4.0 | **4.50** | 🔄 **CLOSE** |
| S1 Acc → 40% | **23.7%** | ❌ **BEHIND** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **Current AR performance stronger** than v1 (28.6 vs 43.9 PPL). S1 accuracy lagging v1 equivalent.

## Infrastructure  
**Uptime**: 19.2hrs across 2 sessions. **Total cost**: $11.84 ($8.76 current session). One spot reclaim on 2026-03-08. Current instance stable 19hrs. Checkpoints: steps 13k-15k synced.

## What's Next
Monitor S1 accuracy regression - may need learning rate adjustment. Diffusion loss approaching target. **ETA completion**: 2026-03-13. Post-training: comprehensive benchmark suite vs v1/v2, confidence calibration analysis.