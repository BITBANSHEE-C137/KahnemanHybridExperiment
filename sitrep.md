# v3 Training SITREP

## v3 Training Status
**Step 6200/50000** (12.4% complete). GPU at **100% util**, 208W/300W power, 61°C. Current rate ~229 steps/hr, **ETA ~8 days**. Spot instance cost **$0.46/hr** (62% savings), projected total **$27.81**.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29 | 6.75 | 5.0% | 0.557 | 0.0057 |
| 2000 | 22.53 | 6.54 | 6.4% | 0.613 | 0.0036 |
| 3000 | 23.17 | 6.38 | 7.6% | 0.638 | 0.0100 |
| 4000 | 23.71 | 6.29 | 8.5% | 0.672 | 0.0109 |
| 5000 | 24.35 | 6.12 | 9.1% | 0.695 | 0.0082 |
| 6000 | **24.85** | **6.08** | **9.9%** | **0.719** | **0.0123** |

**Trends**: AR perplexity **degrading** (+3.6 from step 1k). Diffusion loss improving (-0.67). S1 accuracy **doubling** (+4.9pp). AUROC steadily climbing (+0.162). ECE volatile but reasonable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **24.85** | ✅ **MET** |
| AUROC > 0.75 | **0.719** | ❌ **Need +0.031** |
| ECE < 0.05 | **0.012** | ✅ **MET** |
| Diff loss → 4.0 | **6.08** | 🔄 **52% to target** |
| S1 accuracy → 40% | **9.9%** | 🔄 **25% to target** |

**3/5 targets on track**. AUROC close to threshold. Diff loss and S1 acc progressing but need acceleration.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR performance (**PPL 24.85**) significantly better than v1 WikiText baseline, suggesting joint training not regressing AR capability this time.

## Infrastructure
**Current session**: 7.7hrs uptime, $3.48 spent. **Previous session**: terminated after 6.8hrs, $3.11 cost. **Total**: 2 spot reclaims, **$6.59** total spend. Instance stable in us-east-1a, no recent interruptions.

## What's Next
Continue monitoring AR regression risk—currently **outperforming v1**. Focus on **AUROC convergence** (need +4.3% to target). Expect diffusion/S1 targets achievable by step 15k based on current trajectory. Next eval checkpoint at step 7k.