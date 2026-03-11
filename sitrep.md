# v3 Training SITREP

## v3 Training Status
**81.0% complete** (40,500/50,000 steps) | **98% GPU util** on L4 | **~13.5 steps/min** | **ETA: ~12hrs** | **$0.43/hr spot** (56% savings vs on-demand) | Current session: **1.1hrs uptime**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 33k  | 28.93  | 4.09      | 26.6%   | 0.861 | 0.0086 |
| 34k  | 28.85  | 4.15      | 25.6%   | 0.871 | 0.0069 |
| 35k  | 28.73  | 4.26      | 25.0%   | 0.863 | 0.0057 |
| 36k  | 28.59  | 4.46      | 23.5%   | 0.864 | 0.0109 |
| 37k  | 28.51  | 4.52      | 24.1%   | 0.856 | 0.0065 |
| 38k  | 28.43  | 4.02      | 28.5%   | 0.864 | 0.0092 |
| 39k  | 28.34  | 4.04      | 29.0%   | 0.863 | 0.0113 |
| 40k  | 28.27  | 3.76      | 30.3%   | **0.881** | 0.0094 |

**Trends**: AR PPL steadily improving ✓ | Diff loss volatile but **trending down** ✓ | S1 accuracy **recovering strongly** after dip ✓ | AUROC **jumped to 0.881** at 40k ✓

## Target Scorecard
- **AR PPL < 40**: **28.27** ✅ (crushed target)
- **AUROC > 0.75**: **0.881** ✅ (exceeded)  
- **ECE < 0.05**: **0.0094** ✅ (well calibrated)
- **Diff loss → 4.0**: **3.76** ✅ (trending below target)
- **S1 accuracy → 40%**: **30.3%** ❌ (but improving rapidly)

**4/5 targets met**. S1 accuracy on track to hit 40% by completion.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText-103 PPL 43.86, S1 loss 4.12  
v3 current AR performance (**PPL 28.27**) already **significantly better** than v1 (43.86). Diff loss approaching v1's S1 performance level.

## Infrastructure
**21 spot sessions** | **$32.81 total cost** | Frequent interruptions days 1-2, but **stable 24hr run** yesterday on g6.2xlarge | Current g6.2xlarge instance **1.1hrs uptime** | **56% cost savings** vs on-demand

## What's Next
**9,500 steps remaining** (~12hrs) | Expect S1 accuracy to reach 40%+ | Run final v3 benchmarks | Compare v1→v3 improvements: AR quality, confidence calibration, joint training stability