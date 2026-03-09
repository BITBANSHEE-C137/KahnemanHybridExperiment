# v3 Training SITREP - 2026-03-09 23:30 UTC

## v3 Training Status
**Step 20,800 / 50,000** (41.6% complete)  
**GPU**: A10G @ 99% util, 203W/300W, 56°C, 16.6/23GB VRAM  
**Rate**: ~11.4 steps/min (based on 400 steps in 35 min)  
**ETA**: ~46 hours to completion  
**Spot Cost**: $0.48/hr (60.6% savings), **$17.73 total**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|---------|
| 13000 | 28.41  | 4.42      | 24.1%   | 0.844 | 0.011  |
| 14000 | 28.51  | 4.29      | 24.7%   | 0.852 | 0.009  |
| 15000 | 28.64  | 4.50      | 23.7%   | **0.864** | **0.005** |
| 16000 | 28.66  | 4.38      | 23.5%   | 0.856 | 0.010  |
| 17000 | 28.89  | 4.34      | 25.2%   | 0.858 | 0.008  |
| 18000 | 28.99  | 4.44      | 23.0%   | 0.858 | 0.010  |
| 19000 | 29.21  | 4.39      | 22.1%   | 0.866 | 0.011  |
| 20000 | 29.22  | 4.24      | **26.8%** | 0.857 | 0.005  |

**Trends**: AR PPL slowly degrading (+0.8 over 7k steps). AUROC stable ~0.86. S1 accuracy volatile but improving trend. ECE excellent <0.01.

## Target Scorecard
- **AR PPL < 40**: ✅ **29.22** (on track)
- **AUROC > 0.75**: ✅ **0.857** (exceeding)  
- **ECE < 0.05**: ✅ **0.005** (excellent)
- **Diff loss → 4.0**: ⚠️ **4.24** (close, trending down)
- **S1 accuracy → 40%**: ❌ **26.8%** (needs 13pp improvement)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (29.22) already beats v1 WikiText performance**

## Infrastructure
**18 spot reclaims** - major instability. Current session: 1.2hrs uptime on g5.2xlarge.  
Cost efficiency excellent at **$17.73 total** vs $44 on-demand.  
**Critical**: Excessive spot interruptions slowing progress significantly.

## What's Next
- Monitor S1 accuracy plateau - may need hyperparameter adjustment
- Investigate spot instance selection strategy (AZ/type diversity)  
- Prepare v3 benchmark suite for step 25k checkpoint
- Confidence head analysis on latest eval run