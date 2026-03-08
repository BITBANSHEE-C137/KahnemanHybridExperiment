# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 3300/50000 (6.6%)** | GPU: 100% util, 204W/300W, 60°C | **Rate: ~230 steps/hr** | ETA: ~8.5 days | Spot: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.006 |
| 2000 | 22.53  | 6.54      | 6.44%  | 0.613 | 0.004 |
| 3000 | **23.17** | **6.38** | **7.57%** | **0.638** | **0.010** |

**🔴 AR PPL regressing** (21.29→23.17), **🟢 diffusion loss improving** (-5.5%), **🟢 S1 accuracy climbing** (+50%), **🟢 AUROC trending up** (+14.5%), **🟡 ECE slightly degraded** but still excellent.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **23.17** | ✅ **MET** |
| AUROC > 0.75 | **0.638** | ❌ Need +17.8% |
| ECE < 0.05 | **0.010** | ✅ **MET** |
| Diff loss → 4.0 | **6.38** | ❌ Need -37% |
| S1 accuracy → 40% | **7.57%** | ❌ Need +429% |

**2/5 targets met**. Early stage but concerning AR regression vs improving diffusion.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (23.17) significantly better than v1 WikiText (43.86)**

## Infrastructure
**2 spot sessions**, **0 reclaims** | Total cost: **$4.99** | Current session: 4.2hr uptime | Checkpoints syncing normally | VRAM: 16.2/23GB (70%)

## What's Next
Monitor AR regression trend - may indicate learning rate too aggressive. Expect S1 accuracy acceleration around 5k-10k steps. Planning confidence head ablation at 10k checkpoint.