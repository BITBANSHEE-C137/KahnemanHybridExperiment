# v3 Training SITREP - Step 19400

## v3 Training Status
**Progress**: 19.4k/50k steps (**38.8%**) | **GPU**: 98% util, 189W/300W, 52°C | **Rate**: ~400 steps/hr | **ETA**: ~77 hrs | **Spot Cost**: $0.48/hr (61% savings)

Current instance: g5.2xlarge (A10G, 16.6/23GB VRAM) running 44min, stable.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 12000| 28.12  | 4.31      | 25.0%  | 0.853 | 0.007|
| 13000| 28.41  | 4.42      | 24.1%  | 0.844 | 0.011|
| 14000| 28.51  | 4.29      | 24.7%  | 0.852 | 0.009|
| 15000| 28.64  | 4.50      | 23.7%  | 0.864 | 0.005|
| 16000| 28.66  | 4.38      | 23.5%  | 0.856 | 0.010|
| 17000| 28.89  | 4.34      | 25.2%  | 0.858 | 0.008|
| 18000| 28.99  | 4.44      | 23.0%  | 0.858 | 0.010|
| 19000| 29.21  | 4.39      | 22.1%  | 0.866 | 0.011|

**🔴 AR PPL slowly degrading** (28.1→29.2). **🟡 S1 accuracy volatile**, trending down. **🟢 AUROC stable/improving**. ECE acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **29.21** | ✅ |
| AUROC > 0.75 | **0.866** | ✅ |
| ECE < 0.05 | **0.011** | ✅ |
| Diff loss → 4.0 | **4.39** | 🟡 (needs -0.4) |
| S1 accuracy → 40% | **22.1%** | 🔴 (needs +18pp) |

**3/5 targets met**. S1 accuracy is concerning - **18pp gap** and declining.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% (1.46 PPL), WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

Current v3 AR performance (**29.21 PPL**) is **33% better than v1's 43.86** but still behind GPT-2 baseline.

## Infrastructure
**Cost**: $14.69 total across 5 sessions. **4 spot reclaims** in 3 days - high churn rate. Instance types: g5.2xlarge→g6.xlarge→g5.2xlarge (current). 

**Uptime**: 61% efficiency after accounting for reclaims and restarts.

## What's Next
Continue to 50k steps (~77hr). **Monitor S1 accuracy decline** - may need learning rate adjustment or regularization. Evaluate confidence head calibration. Prepare v1 vs v3 comparison framework for final benchmarks.