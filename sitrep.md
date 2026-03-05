# v2 Training SITREP

## v2 Training Status
**Step 22,900/50,000** (45.8% complete). A10G GPU at **100% util**, 197W/300W, 57°C. **16.6GB/23GB VRAM** used. Current rate ~400 steps/hr. **ETA: ~68 hours**. Spot cost **$0.45/hr** (62.9% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 22000| **30.95** | 4.19 | 27.5% | 0.858 | **0.0096** |
| 21000| 30.88 | 4.85 | 20.7% | 0.851 | 0.0075 |
| 20000| 30.92 | 4.75 | 21.3% | 0.851 | 0.0072 |
| 18000| 30.77 | 4.03 | 27.2% | **0.869** | **0.0060** |

**Trends**: AR PPL stable ~31. S1 accuracy **highly volatile** (20-27%). AUROC peaked at step 18k then regressed. ECE degrading from excellent 0.006 to marginal 0.010.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.95** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.0096** | ✅ **MET** |
| Diff loss → 4.0 | **4.19** | ⚠️ Close |
| S1 accuracy → 40% | **27.5%** | ❌ **MISS** |

**3/5 targets met**. S1 accuracy **significantly underperforming** at 27% vs 40% target.

## v1 Benchmark Baseline  
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.95) substantially better than v1 WikiText (43.86)** but still trails GPT-2 baseline.

## Infrastructure
**11 spot sessions**, $15.80 total cost. Multiple reclaims yesterday (sessions 2-9), but **current session stable 3.3hrs**. g5.2xlarge in us-east-1b at favorable $0.45/hr rate. **Projected v2 completion cost: ~$50** vs $150 on-demand.

## What's Next
**Critical**: S1 accuracy regression needs investigation - volatile 20-27% range suggests training instability. Monitor AUROC decline from step 18k peak. After completion: comprehensive v1/v2 benchmarks, confidence calibration analysis on ECE degradation.