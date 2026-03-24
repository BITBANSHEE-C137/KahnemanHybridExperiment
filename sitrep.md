# v4 Training SITREP

## v4 Training Status
**Step 40,400/75,000** (53.9% complete). GPU at **100% utilization**, A10G running 202W/300W at 56°C. Training rate ~300 steps/hr. **ETA: ~4.8 days**. Current spot rate **$0.44/hr** (63.8% savings vs on-demand).

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 36500| 30.28  | 0.862 | 0.025| 4.097    | 30.3%  |
| 37000| 30.10  | 0.854 | 0.020| 4.337    | 27.7%  |
| 38000| 29.43  | 0.856 | 0.016| 4.382    | 27.7%  |
| 39000| 29.17  | 0.857 | 0.008| 4.082    | 30.5%  |
| **40000**| **29.05** | **0.862** | **0.018** | **3.791** | **32.7%** |

**Trends:** AR PPL steadily improving (-4.1% over 3.5k steps). Diffusion loss volatile but trending down. S1 accuracy recovering after mid-training dip. Confidence calibration excellent (ECE <0.02).

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.05** | ✅ **Met** |
| AUROC > 0.75 | **0.862** | ✅ **Met** |
| ECE < 0.05 | **0.018** | ✅ **Met** |
| Diff loss → 4.0 | **3.791** | ✅ **Met** |
| S1 accuracy → 40% | **32.7%** | ⚠️ **Approaching** |

**4/5 targets met.** S1 accuracy 82% of target, improving trend.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07. **v4 current AR PPL (29.05) matches GPT-2 baseline** - joint training showing no AR regression vs v1.

## Infrastructure
**73 spot sessions**, total cost **$52.78**. Current session: 10hrs uptime, $4.40 spent. Spot market stable in us-east-1e. Historical reclaim rate ~15% (11/73 sessions <1hr). No major interruptions since step 35k.

## What's Next
Training on track for completion by **March 29**. Post-completion: comprehensive v1 vs v4 benchmarks on LAMBADA/WikiText, confidence head analysis on OOD detection, diffusion sample quality evaluation.