# v2 Training SITREP - 2026-03-05T12:30Z

## v2 Training Status
**Step 19,700/50,000** (39.4% complete). A10G @ 100% util, 198W/300W, 52°C, 16.6/23GB VRAM. Current spot rate **$0.44/hr** (64% savings vs on-demand). **ETA: ~18 hours** at current pace. Total runtime: 7.3h across 10 sessions.

## Eval Metrics & Trends
| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|---------|
| 12000 | 29.35 | 0.852 | 0.009 | 4.342 | 25.6% |
| 15000 | 31.05 | 0.852 | 0.014 | 4.328 | 26.1% |
| 18000 | 30.77 | 0.869 | 0.006 | 4.030 | 27.2% |
| **19000** | **30.81** | **0.860** | **0.007** | **4.311** | **24.5%** |

**Trends**: AR PPL stable ~30.8. AUROC peaked at step 18k (0.869), slight regression. **ECE excellent** (<0.01). Diff loss volatile but trending toward target. **S1 accuracy regressed** -2.7% since step 18k.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.81** | ✅ **MET** |
| AUROC > 0.75 | **0.860** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **4.311** | ⚠️ Close (4.030 achieved at step 18k) |
| S1 accuracy → 40% | **24.5%** | ❌ **38% gap**, recent regression |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. **v2 AR performance stronger** than v1 (PPL 30.8 vs 43.9), but **S1 accuracy significantly behind** target (24.5% vs 40% goal).

## Infrastructure
**Current session**: 7.3h uptime, spot cost **$3.18** vs $8.82 on-demand. **10 spot reclaims** across 24h - high churn in us-east-1b yesterday, stable in us-east-1f today. Total project cost: **$13.11**, projected **$19.21** at completion.

## What's Next
S1 accuracy regression needs investigation - **consider learning rate adjustment** or loss weighting. Diff loss close to target but volatile. After v2: comprehensive benchmarks, confidence calibration analysis, v1/v2 head-to-head comparison.