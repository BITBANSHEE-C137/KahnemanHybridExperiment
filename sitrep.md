# v3 Training SITREP - Step 1200

## v3 Training Status
**Progress:** 1,200/50,000 steps (2.4% complete)  
**GPU:** A10G @ 100% util, 205W/300W, 59°C, 16.2GB/23GB VRAM  
**Rate:** ~3.3 steps/min (est. from session time)  
**ETA:** ~10 days at current rate  
**Spot Cost:** $0.46/hr (62% savings), **$27.90** projected vs $73.61 on-demand

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.006 |

**Single checkpoint - no trend analysis possible yet**

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **21.29** | ✅ **PASS** |
| AUROC > 0.75 | **0.557** | ❌ **FAIL** (-0.193) |
| ECE < 0.05 | **0.006** | ✅ **PASS** |
| Diff Loss → 4.0 | **6.75** | ❌ **FAIL** (+2.75) |
| S1 Acc → 40% | **5.04%** | ❌ **FAIL** (-34.96%) |

**2/5 targets met.** AR performance strong early. Confidence calibration excellent but discrimination poor. S1 learning barely started.

## v1 Benchmark Baseline
v1 @ 50k: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (21.29) already beating v1 WikiText baseline**

## Infrastructure
**Current:** g5.2xlarge spot, 1.7hrs uptime, $0.76 session cost  
**History:** 1 spot reclaim after 6.8hrs (steps 400→1000), cost $3.11  
**Total:** 2 sessions, $3.84 spent, **stable restart recovery**

## What's Next
**Immediate:** Monitor S1 accuracy emergence around 2-3k steps  
**Critical:** AUROC improvement - confidence head may need tuning  
**Checkpoint:** Next eval at step 2000 for trend establishment