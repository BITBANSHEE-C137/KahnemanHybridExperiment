# v2 Training SITREP - Step 44.8k

## v2 Training Status
**89.6% complete** (44,800/50,000 steps). A10G at **99% utilization**, 200W power draw. Current rate ~5 steps/min, **ETA ~17 hours**. Spot cost **$0.46/hr** (62% savings vs on-demand). Total session cost: **$28.55**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 37k  | 30.65  | 4.75      | 21.6%   | 0.861 | 0.007 |
| 38k  | 30.44  | 4.28      | 26.7%   | 0.865 | 0.004 |
| 39k  | 30.41  | 3.80      | 30.7%   | 0.863 | 0.007 |
| 40k  | 30.21  | 4.56      | 23.2%   | 0.857 | 0.007 |
| 42k  | 30.08  | 4.07      | 29.0%   | 0.862 | 0.016 |
| 44k  | **29.96** | **4.37** | **25.4%** | **0.865** | **0.016** |

**Trends:** AR perplexity steadily improving. Diffusion loss volatile but trending toward target. **ECE degrading** (0.004→0.016) - calibration concern. S1 accuracy peaked at 39k then regressed.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.96** | ✅ **MET** |
| AUROC | > 0.75 | **0.865** | ✅ **MET** |
| ECE | < 0.05 | **0.016** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.37** | 🔶 **CLOSE** |
| S1 Acc | → 40% | **25.4%** | ❌ **BEHIND** |

**3/5 targets met.** Diffusion loss 9% above target. S1 accuracy **36% below target** - major concern.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **v2 AR already matching WikiText baseline** - strong signal for joint training success.

## Infrastructure
**15 spot sessions**, 62% cost savings vs on-demand. Recent stability: current session running **4.8hr** without reclaim. Cost trajectory: $28.55 actual vs $41.98 projected on-demand. **No recent spot interruptions** - good momentum for final 5k steps.

## What's Next
**5.2k steps remaining** (~17hr). Post-completion: comprehensive v2 benchmarks, head-to-head v1 vs v2 analysis, **confidence calibration deep-dive** (ECE degradation needs investigation). S1 accuracy plateau concerning - may need architecture review.