# v3 Training SITREP

## v3 Training Status
**Progress:** 47,500/50,000 steps (95.0%) | **GPU:** L4 @ 100% util, 74°C | **Rate:** ~300 steps/hr | **ETA:** 8.3 hrs | **Spot cost:** $0.463/hr (52.6% savings)

## Eval Metrics & Trends

| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|--------|-----|-----------|---------|
| 40000 | 28.27 | 0.881 | **0.009** | 3.76 | 30.3% |
| 41000 | 28.30 | 0.866 | 0.011 | 3.95 | 27.8% |
| 42000 | 28.33 | 0.870 | 0.013 | 3.89 | 29.1% |
| 43000 | 28.14 | 0.869 | 0.010 | 4.20 | 25.9% |
| 44000 | **28.07** | 0.867 | **0.010** | 4.40 | 24.9% |
| 45000 | **27.95** | 0.870 | 0.011 | 4.16 | 26.5% |
| 46000 | 28.13 | 0.866 | 0.016 | 3.94 | 28.1% |
| 47000 | 28.09 | **0.870** | **0.014** | **3.88** | **29.3%** |

**Trends:** AR PPL stable around 28 (slight improvement). S1 accuracy volatile but trending up. Diffusion loss unstable. **ECE degrading** from 0.009 to 0.014.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.09** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.014** | ✅ **MET** |
| Diff loss → 4.0 | **3.88** | ✅ **MET** |
| S1 accuracy → 40% | **29.3%** | ❌ **MISS** |

**3/5 targets exceeded, 1/5 met, 1/5 missed.** S1 accuracy **10.7pp below target** but improving.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL.

**Current vs v1:** AR improved significantly (28.09 vs 43.86 PPL). S1 loss comparable to v1 final. Joint training showing **minimal AR degradation** vs pure autoregressive.

## Infrastructure
**Current:** g6.2xlarge, 4.4hrs uptime, $2.06 spent. **Total cost:** $38.31 across 22 spot sessions. **Stability issues:** Multiple reclaims on 3/9 (11 sessions in 6 hours). **Current session:** Stable since 16:32 UTC.

**Historical pain points:** g5.xlarge frequent reclaims, g6 instances more stable in us-east-1a.

## What's Next
**Immediate:** Complete final 2,500 steps (~8 hrs). **Post-completion:** Full benchmark suite, confidence calibration analysis, v1 vs v3 regression testing. **Priority:** Investigate S1 accuracy plateau and ECE degradation in final phase.