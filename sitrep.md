# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 22,100 / 50,000 (44.2%)** - ETA ~28 hrs at current rate  
**GPU**: A10G @ 100% util, 197W/300W, 52°C, 16.6GB/23GB VRAM  
**Rate**: ~2.4 steps/min sustained  
**Spot**: $0.48/hr (60.7% savings), current session 2.7hrs stable

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 15000 | 28.6   | 4.50      | 23.7%  | 0.864 | 0.0052 |
| 18000 | 29.0   | 4.44      | 23.0%  | 0.858 | 0.0098 |
| 20000 | 29.2   | 4.24      | 26.8%  | 0.857 | 0.0048 |
| 21000 | 29.9   | 4.26      | 26.8%  | 0.856 | 0.0116 |
| **22000** | **29.7** | **3.95** | **28.3%** | **0.876** | **0.0039** |

**Trends**: Diff loss **major drop** step 21k→22k (4.26→3.95), AUROC **improved** to 0.876, ECE **excellent** at 0.0039. AR PPL stable ~29-30.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.7** | ✅ **MET** |
| AUROC | > 0.75 | **0.876** | ✅ **MET** |
| ECE | < 0.05 | **0.0039** | ✅ **MET** |
| Diff Loss | → 4.0 | **3.95** | ✅ **MET** |
| S1 Acc | → 40% | **28.3%** | ❌ 11.7% gap |

**4/5 targets met** - only S1 accuracy lagging but trending up.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR performance superior to v1** (29.7 vs 43.86 PPL)

## Infrastructure  
**18 spot sessions**, **17 interruptions** - severe instability 3/9 afternoon/evening  
Total cost: **$18.41** vs $44.23 on-demand (58% savings)  
Current session: 2.7hrs stable, longest recent run  
**Checkpoints**: step_22000.pt (1.5GB) synced successfully

## What's Next
**Diff loss breakthrough** at 22k suggests S2 process converging - monitor S1 accuracy acceleration. Continue to step 25k for stability assessment before benchmark planning.