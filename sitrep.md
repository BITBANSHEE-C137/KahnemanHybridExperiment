# v3 Training SITREP - Step 14,400

## v3 Training Status
**Progress:** 14,400/50,000 steps (28.8% complete)  
**GPU:** A10G @ 100% util, 199W/300W, 44°C, 16.2/23.0GB VRAM  
**Rate:** ~230 steps/hr based on trajectory  
**ETA:** ~6.5 days remaining  
**Spot Cost:** $0.454/hr (62.2% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 7000  | 25.48  | 5.87      | 10.6%   | 0.739 | 0.0089|
| 8000  | 26.29  | 5.60      | 12.6%   | 0.785 | 0.0076|
| 9000  | 26.95  | 5.06      | 18.4%   | 0.805 | 0.0059|
| 10000 | 27.55  | 4.98      | 19.0%   | 0.828 | 0.0053|
| 11000 | 27.85  | 4.43      | 22.0%   | 0.853 | 0.0102|
| 12000 | 28.12  | 4.31      | 25.0%   | 0.853 | 0.0066|
| 13000 | 28.41  | 4.42      | 24.1%   | 0.844 | 0.0110|
| **14000** | **28.51** | **4.29** | **24.7%** | **0.852** | **0.0087**|

**Trends:** AR perplexity degrading (+12% since step 7k). Diffusion loss improving (-27%). S1 accuracy growth stalled at ~24-25%. AUROC strong but volatile. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.51** | ✅ **MET** |
| AUROC > 0.75 | **0.852** | ✅ **MET** |
| ECE < 0.05 | **0.0087** | ✅ **MET** |
| Diff Loss → 4.0 | **4.29** | 🔄 **CLOSE** (7% gap) |
| S1 Acc → 40% | **24.7%** | ❌ **MISS** (38% gap) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current AR performance superior to v1 baseline** (28.5 vs 43.9 PPL)

## Infrastructure
**Current session:** 17.7h uptime, $8.08 spot cost, no interruptions  
**Previous session:** 6.8h, $3.11 cost, terminated after 600 steps  
**Total cost:** $11.20 across 2 sessions  
**Spot stability:** Good - current rate stable at $0.454/hr

## What's Next
**Priority:** S1 token accuracy plateau concerning - only 0.6% gain in last 2k steps. Monitor for training dynamics issues. Diffusion loss trending toward target but AR regression needs investigation. Consider confidence head analysis if S1 stagnation continues.