# v2 Training SITREP - Step 45.6k

## v2 Training Status
**Progress**: 45.6k/50k steps (**91.2%** complete)  
**GPU**: A10G @ 100% util, 197W/300W, 16.6GB/23GB VRAM  
**Rate**: ~2.27 steps/min (400 steps in 2.9h)  
**ETA**: ~32 hours  
**Spot Cost**: $0.46/hr (61.8% savings vs $1.21 on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 38000| 30.44  | 4.28      | 26.7%   | 0.865 | 0.004|
| 40000| 30.21  | 4.56      | 23.2%   | 0.857 | 0.007|
| 42000| 30.08  | 4.07      | 29.0%   | 0.862 | 0.016|
| 44000| 29.96  | 4.37      | 25.4%   | 0.865 | 0.016|
| **45000**| **29.80** | **3.86** | **29.3%** | **0.875** | **0.016**|

**Trends**: AR PPL steadily improving. AUROC recovering after dip at 40k. ECE degraded from excellent early values but stabilizing. S1 accuracy volatile but trending up.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.8** | ✅ **PASS** |
| AUROC  | > 0.75 | **0.875**| ✅ **PASS** |
| ECE    | < 0.05 | **0.016**| ✅ **PASS** |
| Diff Loss| → 4.0| **3.86** | ✅ **PASS** |
| S1 Acc | → 40%  | **29.3%**| ❌ **MISS** |

**4/5 targets met**. S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12  
**v2 vs v1**: AR already superior (29.8 vs 43.86 PPL), diff loss approaching v1 levels. Strong trajectory.

## Infrastructure
**Current**: g5.2xlarge spot (5.8h uptime), 15 total sessions  
**Total Cost**: $29.01 ($26.16 finalized + $2.68 current)  
**Reliability**: Frequent spot reclaims (15 sessions), but good AZ diversity limiting impact  
**Storage**: 1.5GB checkpoints, sync running

## What's Next
**ETA completion**: ~32h at current rate. Post-completion: full v2 benchmarks vs v1/GPT-2, confidence calibration analysis, S1 accuracy deep dive (why underperforming?).