# v3 Training SITREP

## v3 Training Status
**Step 400/50k** (0.8% complete) | **GPU: 100% util** A10G @ 202W/300W, 58°C | **Rate:** ~0.23 steps/s | **ETA:** ~60 hours | **Spot cost:** $0.46/hr (62% savings)

⚠️ **CRITICAL**: Step count regressed from 1000 → 400. Possible checkpoint rollback or instance restart.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | Conf AUROC | ECE |
|------|--------|-----------|--------|------------|-----|
| 1000 | **21.29** | **6.75** | **4.98%** | **0.555** | **0.004** |
| 400  | ~24.0¹ | **7.00** | ~4.5%¹ | ~0.55¹ | ~0.004¹ |

¹*Estimated from current AR loss 3.17*

**Trends:** Diffusion loss **regressed +4%** from checkpoint. AR performance likely degraded with step rollback.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | ~24.0 | ✅ **MET** |
| AUROC > 0.75 | 0.555 | ❌ **MISS** (-26%) |
| ECE < 0.05 | 0.004 | ✅ **MET** |
| Diff loss → 4.0 | 7.00 | ❌ **MISS** (+75%) |
| S1 acc → 40% | 4.98% | ❌ **MISS** (-88%) |

**2/5 targets met.** Confidence and S1 performance significantly behind.

## v1 Benchmark Baseline
v1@50k: LAMBADA 94.26% | WikiText PPL 43.86 | S1 loss 4.12  
Current v3 AR PPL **45% better** than v1 WikiText baseline. Diffusion loss **70% higher** than v1 S1 target.

## Infrastructure
**Current:** g5.2xlarge spot, 39min uptime, $0.26 session cost  
**History:** 2 sessions, 1 completed (6h46m, $3.11), **1 spot reclaim**  
**Total cost:** $3.38 vs $73.28 on-demand

## What's Next
**Immediate:** Investigate step regression - validate checkpoint integrity and resume logic. Monitor for additional spot interruptions.  
**Post-recovery:** Focus on diffusion loss convergence and S1 token accuracy improvements.