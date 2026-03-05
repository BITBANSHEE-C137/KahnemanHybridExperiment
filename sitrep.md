# v2 Training SITREP

## v2 Training Status
**Step 21,700/50,000 (43.4%)** | A10G @ 100% util, 200W/300W | **9.8 hrs remain** @ current 735 steps/hr | Spot: **$0.44/hr** (64% savings) | Total cost: **$14.24**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 14000 | 30.34 | 4.31 | 25.96% | 0.853 | 0.011 |
| 16000 | 30.79 | 4.13 | 26.82% | 0.860 | 0.007 |
| 18000 | 30.77 | 4.03 | 27.23% | **0.869** | 0.006 |
| 20000 | 30.92 | 4.75 | 21.31% | 0.851 | 0.007 |
| 21000 | 30.88 | **4.85** | **20.67%** | 0.851 | 0.007 |

**🔴 Regression Alert:** Diffusion loss increased +21% since step 18k. S1 accuracy dropped 24%. AUROC peaked at 18k then declined.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.88** | ✅ |
| AUROC > 0.75 | **0.851** | ✅ |
| ECE < 0.05 | **0.007** | ✅ |
| Diff loss → 4.0 | **4.85** | ❌ (+21%) |
| S1 accuracy → 40% | **20.7%** | ❌ (declining) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR performance tracking ahead of v1** but **diffusion/S1 performance concerning**.

## Infrastructure
**10 spot reclaims** in 2.5 days. Current session: 9.8h uptime, us-east-1f stable. Instance hopping between us-east-1a/b/f. **$14.20 total** vs $53.37 on-demand. 3 checkpoints stored, 1.5GB each.

## What's Next
**Immediate:** Monitor diffusion loss trend - may need LR adjustment or loss weighting. **Post-completion:** Full v2 benchmarks, analyze confidence head calibration, compare joint training impact vs v1 baselines.