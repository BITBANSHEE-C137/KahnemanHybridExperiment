# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 43,800/50,000 (87.6%)** | GPU: 100% util, 70W/72W, 81°C | Rate: ~300 steps/hr | **ETA: ~21 hours** | Spot: $0.43/hr (56.5% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 36k   | 28.59  | 4.46      | 23.5%  | 0.864 | 0.0109 |
| 37k   | 28.51  | 4.52      | 24.1%  | 0.856 | 0.0065 |
| 38k   | 28.43  | **4.02**  | 28.5%  | 0.864 | 0.0092 |
| 39k   | 28.34  | 4.04      | 29.0%  | 0.863 | 0.0113 |
| 40k   | 28.27  | **3.76**  | 30.3%  | **0.881** | 0.0094 |
| 41k   | 28.30  | 3.95      | 27.8%  | 0.866 | 0.0105 |
| 42k   | 28.33  | 3.89      | 29.1%  | 0.870 | 0.0126 |
| 43k   | **28.14** | 4.20   | 25.9%  | 0.869 | 0.0103 |

**Trends**: AR perplexity steadily improving. Diffusion loss volatile but trending down. S1 accuracy plateaued mid-20s%. AUROC stable ~0.87. ECE excellent <0.015.

## Target Scorecard
- **AR PPL < 40**: ✅ **28.14** (exceeded)
- **AUROC > 0.75**: ✅ **0.869** (strong)  
- **ECE < 0.05**: ✅ **0.010** (excellent calibration)
- **Diff loss → 4.0**: 🔄 **4.20** (close, volatile)
- **S1 accuracy → 40%**: ❌ **25.9%** (stagnant)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance (28.14) significantly better than v1 (43.86)**.

## Infrastructure
**Current**: g6.2xlarge L4, 6.6h uptime, $2.79 session cost. **Total**: 21 sessions, $35.19 spent, multiple spot reclaims early (step 19k-20k instability). Stable since step 24k on g6 instances. **72% VRAM utilization** (16.6GB/23GB).

## What's Next
**6,200 steps remaining** (~21hrs). Watch S1 accuracy - needs 15% jump to hit target. Diffusion loss within striking distance of 4.0. Post-training: comprehensive v1 vs v3 benchmarks, confidence calibration analysis.