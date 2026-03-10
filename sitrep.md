# v3 Training SITREP - Step 23,700

## v3 Training Status
**Progress**: 23,700/50,000 steps (**47.4%** complete)  
**GPU**: A10G @ 100% util, 196W/300W, 52°C, 16.6/23GB VRAM  
**Rate**: ~147 steps/hr (based on current session)  
**ETA**: ~7.5 days remaining  
**Spot Cost**: $0.48/hr (60.7% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|--------|--------|
| 16000 | 28.66  | 4.38      | 23.5%   | 0.856  | 0.0104 |
| 17000 | 28.89  | 4.34      | 25.2%   | 0.858  | 0.0079 |
| 18000 | 28.99  | 4.44      | 23.0%   | 0.858  | 0.0098 |
| 19000 | 29.21  | 4.39      | 22.1%   | 0.866  | 0.0106 |
| 20000 | 29.22  | 4.24      | 26.8%   | 0.857  | 0.0048 |
| 21000 | 29.94  | 4.26      | 26.8%   | 0.856  | 0.0116 |
| 22000 | 29.70  | **3.95**  | 28.3%   | 0.876  | 0.0039 |
| 23000 | **29.57** | 4.19   | 26.1%   | 0.861  | **0.0059** |

**Trends**: AR PPL plateaued ~29; diffusion loss volatile but trending down; S1 accuracy unstable around 25%; AUROC solid >0.85; ECE excellent <0.01.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **29.57** | ✅ **Met** |
| AUROC  | > 0.75 | **0.861** | ✅ **Met** |
| ECE    | < 0.05 | **0.0059** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.19** | 🔶 **Close** |
| S1 Acc | → 40% | **26.1%** | ❌ **Behind** |

**3/5 targets met**. S1 accuracy struggling, diffusion loss near target.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07  

Current v3 AR performance (**PPL 29.57**) significantly better than v1 (43.86), approaching GPT-2 baseline (29.07). S1 progress slower than v1's 67% loss reduction.

## Infrastructure
**Current**: g5.2xlarge spot, 4.7hrs uptime, $2.20 spent this session  
**Total Cost**: **$19.40** across 18 sessions (avg $1.08/session)  
**Instability**: Multiple spot reclaims 3/9 PM - 10/3 PM, causing training interruptions around step 20k. **Stable since 22:18 UTC**.

## What's Next
Training steady on current infrastructure. **Monitor S1 accuracy plateau** - may need hyperparameter adjustment. After v3 completion: comprehensive v1/v2/v3 benchmarks, confidence calibration analysis, diffusion convergence study.