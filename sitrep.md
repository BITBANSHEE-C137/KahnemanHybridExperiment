# v3 Training SITREP

## v3 Training Status
**Step 47,800/50,000** (95.6% complete) • **2,200 steps remaining** • GPU: **100% util**, 83°C, 72W • Current rate: ~300 steps/hr • **ETA: ~7.3 hours** • Spot cost: **$0.463/hr** (52.6% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 40000 | 28.27  | 3.757     | 30.3%   | 0.881 | 0.009 |
| 42000 | 28.33  | 3.892     | 29.1%   | 0.870 | 0.013 |
| 44000 | 28.07  | 4.404     | 24.9%   | 0.867 | 0.010 |
| 46000 | 28.13  | 3.943     | 28.1%   | 0.866 | 0.016 |
| **47000** | **28.09** | **3.883** | **29.3%** | **0.871** | **0.014** |

**Trends:** AR perplexity **stable** around 28. AUROC **declining slightly** from 0.881→0.871. ECE **worsened** from 0.009→0.014. S1 accuracy **volatile** but trending down. Diffusion loss **unstable**.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.09** | ✅ **MET** |
| AUROC > 0.75 | **0.871** | ✅ **MET** |
| ECE < 0.05 | **0.014** | ✅ **MET** |
| Diff loss → 4.0 | **3.88** | ⚠️ **Close** |
| S1 accuracy → 40% | **29.3%** | ❌ **Missing** |

**3/5 targets met.** S1 accuracy **significantly underperforming** vs 40% target.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 AR performance (28.09 PPL) significantly better than v1 (43.86 PPL)** but still behind GPT-2 baseline (29.07).

## Infrastructure
**22 spot sessions**, total cost **$38.54**. Current session: g6.2xlarge, 4.9h uptime, no interruptions. **Stable streak** since 16:33 UTC. Recent session history shows **frequent early terminations** 3/9-3/10 but **improved stability** on current g6.2xlarge instance.

## What's Next
**Training completes in ~7 hours.** Post-completion: v3 LAMBADA/WikiText benchmarks, confidence calibration analysis, v1 vs v3 head-to-head comparison. **Key concern: S1 token accuracy regression** needs investigation.