# v2 Training SITREP - Step 30.3k

## v2 Training Status
**Step 30,300/50,000 (60.6%)** - A10G at **100% util**, 192W/300W, 53°C, 16.6GB/23GB VRAM. Training rate ~400 steps/hr. **ETA: 1.3 days**. Current spot: **$0.45/hr (63% savings)**, session cost $1.33.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 28000 | **31.32** | **3.95** | 28.2% | **0.872** | **0.007** |
| 29000 | 31.43 | 4.21 | 27.7% | 0.860 | 0.022 |
| 30000 | 31.68 | 4.08 | **28.1%** | 0.864 | 0.023 |

**Trends**: AR PPL stable ~31.5. **Confidence AUROC peaked at step 28k** (0.872), regressed slightly. ECE volatile but acceptable. S1 accuracy stuck ~28%.

## Target Scorecard
- **AR PPL < 40**: ✅ **31.7** (strong)
- **AUROC > 0.75**: ✅ **0.864** (good but declining from peak)
- **ECE < 0.05**: ✅ **0.023** (excellent calibration)  
- **Diff loss → 4.0**: ⚠️ **4.08** (close, trending right)
- **S1 accuracy → 40%**: ❌ **28.1%** (plateau, concerning)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v2 AR performance on track** (31.7 vs 43.86), but **S1 progress stalled** at 28% vs v1's 4.12 loss equivalent.

## Infrastructure  
**13 spot sessions, 62.8% savings ($20.30 vs $32.47 on-demand)**. Current instance stable 2.9hr uptime. Historical: 12 spot reclaims but quick recovery. **Checkpoint sync active**, last backup 25min ago.

## What's Next
Training **40% complete** - monitor S1 accuracy breakthrough and AUROC stability. Post-completion: comprehensive v1/v2 benchmarks, confidence head analysis on calibration excellence.