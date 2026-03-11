# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 36,300/50,000 (72.6%)** | GPU: L4 100% util, 82°C, 16.6GB/23GB VRAM | **Rate**: ~480 steps/hr | **ETA**: 29 hours | **Spot cost**: $0.46/hr (53% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 29000 | 29.36 | 4.27 | 25.5% | 0.867 | 0.0118 |
| 30000 | 29.16 | 4.34 | 24.6% | 0.868 | 0.0046 |
| 31000 | 28.95 | 4.47 | 23.3% | 0.871 | 0.0031 |
| 32000 | 29.04 | 4.35 | 24.2% | 0.865 | 0.0089 |
| 33000 | 28.93 | 4.09 | 26.6% | 0.861 | 0.0086 |
| 34000 | 28.85 | 4.15 | 25.6% | 0.871 | 0.0069 |
| 35000 | 28.73 | 4.26 | 25.0% | 0.863 | 0.0057 |
| **36000** | **28.59** | **4.46** | **23.5%** | **0.864** | **0.0109** |

**Trends**: AR PPL steady improvement (~29.4→28.6). Diffusion loss oscillating 4.1-4.5. S1 accuracy volatile, declining trend. AUROC stable ~0.86. ECE erratic but generally improving.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.59** | ✅ **MET** |
| AUROC | > 0.75 | **0.864** | ✅ **MET** |
| ECE | < 0.05 | **0.0109** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.46** | ⚠️ **ABOVE** |
| S1 Accuracy | → 40% | **23.5%** | ❌ **BELOW** |

**3/5 targets met**. Diffusion loss needs 0.46 improvement. S1 accuracy 16.5% short of target.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL

Current v3 AR PPL (**28.59**) already **beats v1** (43.86) and approaches GPT-2 baseline (29.07). Diffusion loss (4.46) similar to v1 S1 loss (4.12).

## Infrastructure
**Current**: g6.2xlarge, 21hr uptime, $9.68 session cost
**History**: 19 sessions, extreme spot volatility 3/9 (13 reclaims in 6hrs), stabilized since 3/10
**Total cost**: $29.67 across 75k training seconds

## What's Next
**13.7k steps remaining** (~29hr). Monitor S1 accuracy regression - may need learning rate adjustment. Post-v3: comprehensive benchmarks, v1→v3 comparison, confidence calibration analysis on final checkpoints.