## v3 Training Status
**Step 24,800 / 50,000** (49.6% complete). GPU at **100% util**, L4 running hot at **81°C**. Current rate ~5 steps/min. **ETA: ~3.5 days**. Spot cost **$0.46/hr** (53% savings), projected total **$20.21**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.008 |
| 18000 | 28.99 | 4.44 | 23.0% | 0.858 | 0.010 |
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.011 |
| 20000 | 29.22 | **4.24** | 26.8% | 0.857 | **0.005** |
| 21000 | 29.94 | 4.26 | 26.8% | 0.856 | 0.012 |
| 22000 | 29.70 | **3.95** | **28.3%** | **0.876** | **0.004** |
| 23000 | 29.57 | 4.19 | 26.1% | 0.861 | 0.006 |
| 24000 | 29.53 | 4.31 | 25.2% | 0.862 | 0.005 |

**Trends**: AR PPL plateaued ~29. **Diff loss volatile** (3.95→4.31). S1 accuracy peaked at step 22k then regressed. AUROC solid around 0.86. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.53** | ✅ **MET** |
| AUROC > 0.75 | **0.862** | ✅ **MET** |
| ECE < 0.05 | **0.005** | ✅ **MET** |
| Diff loss → 4.0 | **4.31** | ❌ **Above target** |
| S1 accuracy → 40% | **25.2%** | ❌ **Well below** |

**3/5 targets met**. Diffusion loss unstable, S1 accuracy concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR PPL (29.53) much better than v1 (43.86)** but still trails GPT-2. S1 performance lagging v1's 4.12 loss equivalent.

## Infrastructure
**19 spot sessions**, chronic instability around steps 20k-21k with **8 rapid reclaims**. Current g6.2xlarge stable for 1.5hrs. Total cost **$20.71** vs projected **$20.21**. VRAM at 72% (16.6GB/23GB).

## What's Next
**Watch S1 accuracy regression** - may need learning rate adjustment. Diffusion loss needs stabilization before v2 completion. Plan comprehensive benchmarks at step 50k vs v1 baselines.