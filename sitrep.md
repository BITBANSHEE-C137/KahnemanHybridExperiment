# SITREP v2 Training - Step 48900/50000

## v2 Training Status
**97.8% complete** (48900/50000). GPU util **99%** on A10G (50°C, 16.6/23GB VRAM). Current spot rate **$0.46/hr** (61.8% savings vs on-demand). ETA **~2 hours** at current pace.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 41000 | 30.12 | 4.47 | 25.1% | 0.862 | 0.012 |
| 42000 | 30.08 | 4.07 | **29.0%** | 0.862 | 0.016 |
| 43000 | 29.96 | **3.93** | 29.2% | **0.868** | 0.020 |
| 44000 | 29.96 | 4.37 | 25.4% | 0.865 | 0.016 |
| 45000 | 29.80 | 3.86 | 29.3% | **0.875** | 0.016 |
| 46000 | **29.74** | 4.15 | 26.2% | 0.865 | **0.011** |
| 47000 | 29.72 | 4.61 | 22.7% | 0.855 | 0.011 |
| 48000 | 29.72 | **4.73** | **21.9%** | 0.858 | 0.012 |

**Trends:** AR PPL plateaued at ~29.7. **Diffusion loss regressing** from 3.86 → 4.73. **S1 accuracy declining** from 29% peak to 22%. AUROC stable ~0.86. ECE excellent <0.02.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.72** | ✅ |
| AUROC | > 0.75 | **0.858** | ✅ |
| ECE | < 0.05 | **0.012** | ✅ |
| Diff Loss | → 4.0 | **4.73** | ❌ |
| S1 Accuracy | → 40% | **21.9%** | ❌ |

**3/5 targets met**. Diffusion and S1 both regressing in final phase.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 AR already superior to v1** (29.72 vs 43.86 PPL).

## Infrastructure
Current session: **9.8 hrs uptime**, $4.50 cost. **15 spot interruptions** total, $30.83 cumulative cost (vs $47.16 on-demand). No recent interruptions - stable since 17:42 UTC yesterday.

## What's Next
Training completes in ~2 hrs. **Priority:** investigate diffusion/S1 regression in final checkpoints. Run full v2 benchmarks, compare AR improvement vs S1 degradation from v1.