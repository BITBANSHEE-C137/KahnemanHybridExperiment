# v2 Training SITREP

## v2 Training Status
**Step 26,800/50,000 (53.6%)** - A10G running at **100% GPU util**, 197W/300W power. VRAM: 16.6/23.0 GB used. Current rate ~1.95 steps/min. **ETA: ~19.7 hours**. Spot cost: **$0.45/hr** (62.9% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.007  |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007  |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007  |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010  |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010  |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005  |
| 25000 | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012  |
| 26000 | **31.46** | **4.06** | **28.0%** | **0.863** | **0.018** |

**Trends**: AR PPL plateaued ~31 (slight regression). Diffusion loss volatile but trending toward target. S1 accuracy recovering after dip at 20k-21k. **ECE degrading** - confidence calibration worsening.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.46** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.018** | ✅ **MET** |
| Diff loss → 4.0 | **4.06** | ⚠️ **CLOSE** |
| S1 accuracy → 40% | **28.0%** | ❌ **MISS** |

**3/5 targets met**. Diffusion loss nearly at target. S1 accuracy trending up but needs +12pp.

## v1 Benchmark Baseline  
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. v2 AR performance similar to v1 (31.46 vs baseline ~30-31 range). S1 showing improvement trajectory.

## Infrastructure
**12 spot sessions**, 11 reclaims. Current session: 3.6h uptime, $1.59 cost. **Total project cost: $18.07** (vs $38.42 on-demand). Recent stability good - running 3.6h without interruption in us-east-1a.

## What's Next
At current rate: completion by **March 6 evening**. Post-completion: v2 benchmarks on LAMBADA/WikiText, detailed v1 vs v2 comparison, confidence calibration analysis (ECE regression concerning). Monitor S1 accuracy trajectory - may need extended training if plateau persists.