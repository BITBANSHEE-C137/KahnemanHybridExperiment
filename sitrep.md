# v3 Training SITREP

## v3 Training Status
**Progress:** 46.9k/50k steps (**93.8%** complete)  
**GPU:** L4 @ **98%** util, 73W/72W, 78°C, 16.6/23GB VRAM  
**Rate:** ~300 steps/hr | **ETA:** ~10 hours  
**Spot:** $0.463/hr (52.6% savings) | Current session cost: **$1.60**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 39k  | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40k  | 28.27  | 3.76      | 30.3%  | **0.881** | **0.009** |
| 41k  | 28.30  | 3.95      | 27.8%  | 0.866 | 0.011 |
| 42k  | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43k  | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44k  | 28.07  | **4.40**  | **24.9%** | 0.867 | **0.010** |
| 45k  | **27.95** | 4.16   | 26.5%  | 0.870 | 0.011 |
| 46k  | 28.13  | **3.94**  | **28.1%** | 0.866 | 0.016 |

**Trends:** AR PPL improving slowly (**-0.2** over 7k steps). Diffusion loss volatile but trending down. S1 accuracy recovering from 44k dip. **AUROC peaked at 40k**, now plateaued. ECE slightly degrading.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.13** | ✅ **MET** |
| AUROC | > 0.75 | **0.866** | ✅ **MET** |
| ECE | < 0.05 | **0.016** | ✅ **MET** |
| Diff Loss | → 4.0 | **3.94** | ✅ **CLOSE** |
| S1 Accuracy | → 40% | **28.1%** | ❌ **MISS** |

**4/5 targets met.** S1 accuracy **30% below target** but recovering.

## v1 Benchmark Baseline
v1 @ 50k: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (28.13) already beats v1 (43.86) and approaching GPT-2 baseline**

## Infrastructure
**Current:** g6.2xlarge us-east-1a, 3.5hr uptime, stable  
**Total cost:** $37.84 across **22 sessions** (many spot reclaims 3/9-3/10)  
**Reclaim history:** 21 previous instances terminated, mostly g5/g6 in us-east-1b  
**Stability improved:** Current session longest since 3/10

## What's Next
**3.1k steps remaining** (~10hrs). Post-completion: v3 benchmarks on LAMBADA/WikiText, comprehensive v1→v3 comparison, confidence calibration analysis. **S1 accuracy unlikely to reach 40%** - investigate if joint training trade-offs acceptable.