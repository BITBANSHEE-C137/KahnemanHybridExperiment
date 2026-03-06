# v2 Training SITREP

## v2 Training Status
**Step 44,400/50,000** (88.8% complete)  
GPU: **100% utilization**, A10G @ 201W/300W, 51°C, 16.6GB/23GB VRAM  
Rate: ~375 steps/hour | **ETA: ~15 hours**  
Spot cost: **$0.46/hr** (61.8% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 37k  | 30.65  | 4.75      | 21.6%   | 0.861 | 0.007 |
| 38k  | 30.44  | 4.28      | 26.7%   | 0.865 | 0.004 |
| 39k  | 30.41  | 3.80      | 30.7%   | 0.863 | 0.007 |
| 40k  | 30.21  | 4.56      | 23.2%   | 0.857 | 0.007 |
| 44k  | **29.96** | 4.37   | 25.4%   | 0.865 | 0.016 |

**AR perplexity trending down** (-2% since 37k). **Diffusion loss unstable** but improving overall. **S1 accuracy volatile** 21-31% range. **AUROC steady** ~0.86. **ECE degrading** (+130% since 38k).

## Target Scorecard
- ✅ **AR PPL < 40**: 29.96 (ACHIEVED)
- ✅ **AUROC > 0.75**: 0.865 (ACHIEVED) 
- ❌ **ECE < 0.05**: 0.016 (ACHIEVED but trending worse)
- ❌ **Diff loss → 4.0**: 4.37 (close, volatile)
- ❌ **S1 accuracy → 40%**: 25.4% (needs +58% improvement)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v2 AR performance superior to v1** (29.96 vs 43.86 PPL). S1 task still learning.

## Infrastructure
**15 sessions, 14 spot reclaims** across us-east-1a/b/f zones  
Total cost: **$28.28** vs $71.65 on-demand (60% savings)  
Current session: 4.3hr uptime, stable since 17:42 UTC  
Longest session: 15.9hr (i-01351ca), most productive period

## What's Next
**5.6k steps remaining**: confidence head calibration critical - **ECE regression** needs attention. After completion: comprehensive v1 vs v2 benchmarks, confidence analysis deep-dive, production readiness assessment.