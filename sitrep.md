# v3 Training SITREP

## v3 Training Status
**Step 36,000/50,000** (72% complete). GPU maxed at **100% util** on L4, running hot at 80°C, 72W power draw. Rate: ~390 steps/hr. **ETA: 36 hours** to completion. Current spot rate: **$0.46/hr** (53% savings), projected total cost **$20.43**.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 29k   | 29.36  | 4.266     | 25.5%  | 0.867 | 0.012 |
| 30k   | 29.16  | 4.337     | 24.6%  | 0.868 | 0.005 |
| 31k   | 28.95  | 4.469     | 23.3%  | 0.871 | 0.003 |
| 32k   | 29.04  | 4.350     | 24.2%  | 0.865 | 0.009 |
| 33k   | 28.93  | 4.085     | 26.6%  | 0.861 | 0.009 |
| 34k   | 28.85  | 4.149     | 25.6%  | 0.871 | 0.007 |
| 35k   | 28.73  | 4.259     | 25.0%  | 0.863 | 0.006 |
| 36k   | **28.59** | **4.463** | **23.5%** | **0.864** | **0.011** |

**AR perplexity trending down** consistently. **Diff loss volatile** but generally improving. **S1 accuracy regressing** - concerning drop to 23.5%. AUROC stable ~0.86. ECE spiked back up to 0.011.

## Target Scorecard
- ✅ **AR PPL < 40**: 28.59 (BEAT)
- ✅ **AUROC > 0.75**: 0.864 (BEAT)
- ❌ **ECE < 0.05**: 0.011 (BEAT but worsening)
- ❌ **Diff loss -> 4.0**: 4.463 (12% over target)
- ❌ **S1 accuracy -> 40%**: 23.5% (41% below target)

**3/5 targets met**. S1 accuracy significantly underperforming.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, 1.46 PPL | WikiText-103 43.86 PPL | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08% | WikiText 29.07 PPL
Current v3 AR performance **ahead of v1** (28.59 vs 43.86 PPL). S1 performance **unclear** - using different metric (accuracy vs loss).

## Infrastructure
**19 spot sessions**, $29.48 total cost. Current session: 20.6hrs uptime, no interruptions. Heavy churn through steps 20-24k with **8 reclaims** - spot instability resolved around step 25k. Now stable on g6.2xlarge in us-east-1a.

## What's Next
**Critical**: S1 token accuracy regression needs investigation - dropped 2% in last 1k steps. Monitor diff loss volatility. After completion: full benchmark suite, confidence calibration analysis, v1 comparison on standardized metrics.