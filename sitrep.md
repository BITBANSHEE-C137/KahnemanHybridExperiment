# v3 Training Status

**Step 23,300/50,000 (46.6%)** | GPU: **98% util**, A10G 195W/300W, 51°C | VRAM: 16.6/23GB  
Training rate: ~5.8 steps/min | **ETA: ~76 hours** | Current spot: **$0.48/hr** (60.7% savings)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 20000 | 29.22 | 4.235 | 26.8% | 0.857 | 0.0048 |
| 21000 | 29.94 | 4.262 | 26.8% | 0.856 | 0.0116 |
| 22000 | **29.70** | **3.945** | **28.3%** | **0.876** | **0.0039** |
| 23000 | **29.57** | 4.192 | 26.1% | 0.861 | 0.0059 |

**Trends:** AR PPL stable ~29.5. **Diff loss volatile** (3.95→4.19). S1 accuracy regressed from 28.3%→26.1%. AUROC peaked at 22k then dropped. ECE excellent at 22k.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.57** | ✅ **MET** |
| AUROC > 0.75 | **0.861** | ✅ **MET** |
| ECE < 0.05 | **0.0059** | ✅ **MET** |
| Diff loss → 4.0 | **4.19** | 🔄 Close |
| S1 accuracy → 40% | **26.1%** | ❌ Need +14% |

**3/5 targets met.** S1 accuracy lagging significantly.

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (29.57) significantly better than v1 (43.86)**

## Infrastructure

**18 spot reclaims** since Mar 8. Current session: 4.2hrs uptime on g5.2xlarge us-east-1b.  
Total cost: **$19.12** vs $44.27 on-demand (**57% savings**). Heavy instance churn around step 20k.  
Checkpoints: 21k, 22k, 23k stored. Trainer/sync stable.

## What's Next

Monitor S1 accuracy regression. **Diff loss volatility** concerning - step 22k showed promise at 3.95. Consider checkpoint rollback if S1 doesn't recover. Current trajectory suggests **26-28 more hours** to next major eval milestone.