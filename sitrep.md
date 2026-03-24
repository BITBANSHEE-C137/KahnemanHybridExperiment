# v4 Training SITREP

## v4 Training Status
**Step 40,100 / 75,000** (53.5% complete). A10G at 100% utilization, 203W/300W limit, 56°C. Training rate stable, **ETA ~34k more steps**. Current spot rate **$0.44/hr** (63.8% savings vs on-demand). Total run cost **$52.60**.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 36500 | 30.28  | 4.10      | 30.3%  | 0.862 | 0.025 |
| 37000 | 30.10  | 4.34      | 27.7%  | 0.854 | 0.020 |
| 38000 | 29.43  | 4.38      | 27.7%  | 0.856 | 0.016 |
| 39000 | 29.17  | 4.08      | 30.5%  | 0.857 | 0.008 |
| **40000** | **29.05** | **3.79** | **32.7%** | **0.862** | **0.018** |

**Strong progress**: AR perplexity steadily decreasing (-1.2 pts), S1 accuracy climbing (+2.4%), diffusion loss volatile but trending down (-0.3). AUROC stable ~0.86, ECE low and stable.

## Target Scorecard
- ✅ **AR PPL < 40**: 29.05 (exceeded by 27%)
- ✅ **AUROC > 0.75**: 0.862 (exceeded by 15%)
- ✅ **ECE < 0.05**: 0.018 (well under threshold)
- ❌ **Diff loss → 4.0**: 3.79 (approaching target)
- ❌ **S1 accuracy → 40%**: 32.7% (82% of target)

**3/5 targets met**. Diffusion loss nearly there, S1 accuracy improving steadily.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, 1.46 PPL; WikiText-103 43.86 PPL; S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **v4 current AR performance (29.05 PPL) significantly better than v1 (43.86) and approaching GPT-2 baseline**.

## Infrastructure
**73 spot sessions**, aggressive cost optimization. Recent stability: current g5.2xlarge instance running **9.5 hours** uninterrupted. Historical issues with frequent reclaims (sessions 19-42 had <1hr uptimes). **Total accumulated cost $52.60** vs $88.45 on-demand equivalent.

## What's Next
Monitor diffusion loss convergence and S1 accuracy trajectory. Target completion at step 75k in ~35k steps. Post-completion: comprehensive v1 vs v4 benchmarks, confidence calibration analysis, and dual-process effectiveness evaluation.