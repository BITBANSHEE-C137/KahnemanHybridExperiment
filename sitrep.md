# v3 Training SITREP

## v3 Training Status
**Step 2100/50000 (4.2%)** | GPU: 100% util, 205W/300W, 59°C | **Rate**: ~228 steps/hr | **ETA**: ~9.1 days | **Spot cost**: $0.46/hr (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 1000 | 21.29 | 6.75 | 5.04% | 0.557 | 0.0057 |
| 2000 | **22.53** | 6.54 | **6.44%** | **0.613** | **0.0036** |

**Trends**: AR PPL **regressing** (+1.24), S1 accuracy improving (+1.4%), AUROC trending up (+0.056), ECE improving (-0.002). Diffusion loss stable decline.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **22.53** | ✅ **MET** |
| AUROC > 0.75 | **0.613** | ❌ Need +0.137 |
| ECE < 0.05 | **0.0036** | ✅ **MET** |
| Diff loss → 4.0 | **6.54** | ❌ Need -2.54 |
| S1 accuracy → 40% | **6.44%** | ❌ Need +33.6% |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (22.53) significantly better than v1 WikiText (43.86)**

## Infrastructure
**Current session**: 2.7hrs uptime, $1.22 spent | **Previous**: 6.8hrs, terminated at step 1000  
**Total cost**: $4.30 across 2 spot sessions | No spot reclaims during active training  
**Storage**: 1.5GB checkpoints, sync active

## What's Next
**Immediate**: Monitor AR PPL regression - may need LR adjustment if trend continues  
**Post-v2**: Full benchmark suite, confidence calibration analysis, v1/v2/v3 comparison study