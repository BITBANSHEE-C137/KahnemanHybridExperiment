# v3 Training SITREP

## v3 Training Status
**Step 9,100/50,000 (18.2%)** • GPU: 100% util, 206W/300W, 57°C • Rate: ~227 steps/hr • **ETA: 7.5 days** • Spot cost: **$0.458/hr** (62% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|--------|
| 2000 | 22.53 | 0.613 | 0.004 | 6.543 | 6.4% |
| 5000 | 24.35 | 0.695 | 0.008 | 6.121 | 9.1% |
| 7000 | 25.48 | 0.739 | 0.009 | 5.870 | 10.6% |
| 8000 | 26.29 | 0.785 | 0.008 | 5.597 | 12.6% |
| **9000** | **26.95** | **0.805** | **0.006** | **5.061** | **18.4** |

**🔥 Strong acceleration**: S1 accuracy jumped +46% in 1k steps. AUROC crossed 0.8 threshold. AR PPL climbing but within expected range for joint training.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **26.95** | ✅ **PASS** |
| AUROC > 0.75 | **0.805** | ✅ **PASS** |
| ECE < 0.05 | **0.006** | ✅ **PASS** |
| Diff loss → 4.0 | **5.061** | 🟡 74% there |
| S1 accuracy → 40% | **18.4%** | 🟡 46% there |

**3/5 targets met**. Diffusion and S1 both trending strongly toward targets.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL

Current v3 AR performance **superior to v1** (26.95 vs 43.86 PPL). S1 system developing rapidly.

## Infrastructure
**Current session**: 11.2hr uptime, no spot reclaims  
**Total cost**: $8.20 across 2 sessions (1 reclaim at step 1000)  
**Projected cost**: $27.81 to completion vs $73.54 on-demand

## What's Next
Continue training - strong momentum on S1 breakthrough. Next eval at 10k should show S1 >20%. Monitor AR PPL ceiling (~30-35 expected). Prepare v3 vs v1 benchmark suite.