# v2 Training SITREP

## v2 Training Status
**Step 15,900/50,000** (31.8% complete) • **98% GPU util** • A10G @ 52°C, 16.6GB VRAM used • Current rate ~1.9 steps/min • **ETA: ~18 days** • Spot cost **$0.44/hr** (63.9% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 8000 | 27.58 | 4.65 | 21.1% | 0.845 | 0.007 |
| 10000| 28.39 | 4.37 | 25.1% | 0.850 | 0.004 |
| 12000| 29.35 | 4.34 | 25.6% | 0.852 | 0.009 |
| 15000| **31.05** | **4.33** | **26.1%** | **0.852** | **0.014** |

**Concerning trends:** AR PPL degrading (+12.6% since step 8k), ECE slowly rising. Diffusion loss stable. S1 accuracy plateaued ~25%.

## Target Scorecard
- ❌ **AR PPL < 40**: 31.05 (✓ met, but trending worse)
- ✅ **AUROC > 0.75**: 0.852 
- ✅ **ECE < 0.05**: 0.014
- ❌ **Diff loss → 4.0**: 4.33 (stalled)
- ❌ **S1 accuracy → 40%**: 26.1% (plateaued)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12. Current v2 AR PPL (31.05) **better than v1 WikiText baseline** but **S1 accuracy severely lagging** (26% vs target 40%).

## Infrastructure
**10 spot interruptions** in 72hrs - aggressive reclaim rate. Total cost **$11.18** across sessions. Current instance stable 2.8hrs. Mixed g5.xlarge/2xlarge usage due to availability.

## What's Next
**Red flags:** AR degradation + S1 plateau suggest learning rate or architecture issues. Consider LR schedule adjustment. After v2: detailed v1/v2 comparison on LAMBADA, confidence head ablation study.