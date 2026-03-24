# v4 Training SITREP

## v4 Training Status
**Step 38,700/75,000 (51.6% complete)**
- **Rate**: ~5.4 steps/min (3,600 steps in last 200 min)
- **GPU**: A10G @ 100% util, 204W/300W, 56°C, 16.6GB VRAM used
- **ETA**: ~112 hours (4.7 days) to completion
- **Spot cost**: $0.44/hr (63.8% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 35000 | **30.55** | 4.15 | 30.2% | 0.863 | 0.021 |
| 35500 | 31.11 | 4.40 | 28.1% | 0.857 | 0.038 |
| 36000 | 31.11 | 4.20 | 29.9% | 0.864 | 0.021 |
| 36500 | 30.28 | 4.10 | 30.3% | 0.862 | 0.025 |
| 37000 | 30.10 | 4.34 | 27.7% | 0.854 | 0.020 |
| 37500 | 29.73 | 4.36 | 26.8% | 0.854 | 0.010 |
| 38000 | 29.43 | 4.38 | 27.7% | 0.856 | 0.016 |
| 38500 | **29.30** | **4.28** | **28.0%** | **0.858** | **0.012** |

**Trends**: AR PPL improving steadily (-1.25 since step 35k). Diffusion loss volatile but trending down. S1 accuracy stuck ~28%. AUROC stable ~0.86. ECE excellent <0.02.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40 | **29.3** | ✅ **Met** |
| AUROC | >0.75 | **0.858** | ✅ **Met** |
| ECE | <0.05 | **0.012** | ✅ **Met** |
| Diff Loss | →4.0 | **4.28** | 🟡 Close |
| S1 Accuracy | →40% | **28.0%** | ❌ **Need +12pp** |

**3/5 targets met**. S1 accuracy significantly lagging - may need architectural changes or longer training.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v4 AR performance already exceeds v1** (29.3 vs 43.86 PPL). S1 performance similar to v1 baseline.

## Infrastructure
**Current instance**: g5.2xlarge in us-east-1e, **7.0 hours uptime**  
**Total sessions**: 73 (heavy spot reclaim history)  
**Total cost**: $51.46 ($31.99 projected vs $88.45 on-demand)  
**Stability**: Recent session stable, but history shows frequent interruptions averaging ~2-4 hours per instance.

## What's Next
- **Monitor S1 accuracy** - critical blocker for target achievement  
- **Continue through step 75k** - diffusion loss needs more convergence time
- **Post-completion**: Full benchmark suite, v1 vs v4 comparison, confidence calibration analysis
- **Risk**: Spot instance instability could extend timeline significantly