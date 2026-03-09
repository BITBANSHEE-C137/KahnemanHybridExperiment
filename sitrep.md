# v3 Training SITREP

## v3 Training Status
**Step 0/50,000** (0.0% complete) - Fresh boot after spot reclaim
- GPU: A10G @ 100% util, 187W/300W, 16.6GB/23GB VRAM
- Rate: **Unknown** (just started)
- ETA: **TBD** (need rate calculation)
- Spot cost: **$0.48/hr** (61% savings vs $1.21 on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 12000 | 28.12 | 4.31 | 25.0% | 0.853 | 0.007 |
| 15000 | 28.64 | 4.50 | 23.7% | **0.864** | **0.005** |
| 18000 | 28.99 | 4.44 | 23.0% | 0.858 | 0.010 |
| 19000 | **29.21** | 4.39 | **22.1%** | **0.866** | 0.011 |

**Trends:** AR PPL **degrading** (+3.8% over 7k steps). S1 accuracy **declining** (-11.6%). AUROC **improving** (+1.5%). ECE **volatile** but acceptable.

## Target Scorecard
- AR PPL < 40: **✓ 29.2** (PASS - but trending wrong way)
- AUROC > 0.75: **✓ 0.866** (PASS - trending up)  
- ECE < 0.05: **✓ 0.011** (PASS - volatile)
- Diff loss → 4.0: **⚠️ 4.39** (9.8% above target)
- S1 accuracy → 40%: **❌ 22.1%** (FAIL - 45% below target)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
Current v3 AR performance **33% better** than v1 WikiText (29.2 vs 43.86), but S1 accuracy **46% worse** than target.

## Infrastructure
**5 spot sessions, 4 reclaims in 3 days:**
- Session 1-2: g5.2xlarge (steps 400-19300) - $13.8k steps, stable
- Session 3-4: g6.xlarge failures - minimal progress, **2 quick reclaims**
- Session 5: Current g5.2xlarge - just booted

**Total cost: $14.45** | **Current uptime: 13min** | Checkpoints: 17k, 18k, 19k available

## What's Next  
**Immediate:** Resume from step 19k checkpoint, monitor AR PPL trend reversal
**Critical:** S1 accuracy severely underperforming - may need hyperparameter adjustment
**Post-training:** Full v1 vs v3 benchmark comparison once complete