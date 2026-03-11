# SITREP: v3 Training Status - Step 42.6K

## v3 Training Status
**Progress:** 42.6K/50K steps (85.2%) • **Rate:** ~1.6 steps/sec • **ETA:** ~3h remaining  
**GPU:** L4 @ 100% util, 72W, 16.6GB VRAM used • **Spot:** $0.43/hr (56% savings) • **Session cost:** $1.97

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 40000| **28.27** | 3.76 | 30.3% | **0.881** | 0.009 |
| 41000| 28.30 | 3.95 | 27.8% | 0.866 | 0.011 |
| 42000| **28.33** | **3.89** | **29.1%** | **0.870** | **0.013** |

**Trends:** AR PPL plateaued at ~28.3. AUROC peaked at 40K then regressed. ECE degrading slightly. Diff loss improving toward target.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.33** | ✅ **Met** |
| AUROC > 0.75 | **0.870** | ✅ **Met** |
| ECE < 0.05 | **0.013** | ✅ **Met** |
| Diff loss → 4.0 | **3.89** | ✅ **Met** |
| S1 accuracy → 40% | **29.1%** | ❌ **Missing by 11%** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Analysis:** v3 AR performance significantly better than v1 (28.3 vs 43.9 PPL). S1 still underperforming vs target.

## Infrastructure
**Current:** g6.2xlarge, us-east-1b, 4.6h uptime  
**History:** 21 sessions, 12 spot reclaims, frequent instance type switching due to capacity  
**Total cost:** $34.34 across all sessions • **Savings:** 56.5% vs on-demand

## What's Next
Complete v3 training (~7.4K steps remaining). Run full benchmark suite. **Priority:** Investigate S1 accuracy plateau - may need confidence head rebalancing or different loss weighting in final steps.