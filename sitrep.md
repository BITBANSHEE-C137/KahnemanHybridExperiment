# v2 Training Status SITREP

## v2 Training Status
**Step 32,300/50,000 (64.6%)** | GPU: **97% util** A10G @ 53°C, 16.6/23GB VRAM | Rate: ~400 steps/hr | **ETA: 44h** | Spot: **$0.45/hr** (62.8% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 28000| 31.32  | **3.95**  | 28.2%  | **0.872** | **0.007** |
| 29000| 31.43  | 4.21      | 27.7%  | 0.860     | 0.022 |
| 30000| 31.68  | 4.08      | 28.1%  | 0.864     | 0.023 |
| 31000| 31.60  | 4.49      | 24.5%  | 0.862     | 0.014 |
| 32000| **31.39** | **3.96** | **28.4%** | **0.871** | **0.013** |

**Trends**: AR PPL stable ~31.4 (**good**). Diffusion loss volatile but trending down. AUROC recovering after dip. ECE well-controlled. S1 accuracy inconsistent around 28%.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.39** | ✅ **MET** |
| AUROC > 0.75 | **0.871** | ✅ **MET** |
| ECE < 0.05 | **0.013** | ✅ **MET** |
| Diff loss → 4.0 | **3.96** | ✅ **MET** |
| S1 accuracy → 40% | **28.4%** | ❌ **71% of target** |

**4/5 targets met**. S1 accuracy remains problematic, stuck in 24-28% range.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v2 showing AR improvement** (31.4 vs 43.9 PPL) but **S1 regression** (28% vs baseline expectations from 4.12→3.96 loss improvement).

## Infrastructure
**Current session**: 5.5h uptime, $2.42 cost. **Total: 13 sessions, $21.44 cost** across 3 AZs. **8 spot reclaims** (volatile market). No training interruptions - checkpointing robust. Projected total: **~$33** (vs $163 on-demand).

## What's Next
**17.7k steps remaining** (~44h). Focus: **S1 accuracy breakthrough needed** - consider LR adjustment or curriculum changes. Post-completion: comprehensive v1/v2 benchmarks, confidence calibration deep-dive, cost-performance analysis.