# v2 Training SITREP

## v2 Training Status
**Step 29.5k/50k (59%)** | GPU: 100% util, 193W/300W, 54°C | **41 steps/hour** | ETA: **21 hours** | Spot: **$0.45/hr** (63% savings)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|--------|-----|
| 22k  | 30.95  | 4.19      | 27.5%  | 0.858  | 0.010 |
| 25k  | 31.22  | 4.20      | 27.6%  | 0.860  | 0.012 |
| 27k  | 31.46  | **4.48**  | **24.4%** | 0.862  | 0.009 |
| 28k  | 31.32  | **3.95**  | 28.2%  | **0.872** | 0.007 |
| 29k  | **31.43** | 4.21   | 27.7%  | 0.860  | **0.022** |

**⚠️ Volatility**: Diffusion loss swinging ±0.5. S1 accuracy dropped 4pp at step 27k. ECE spiked 3x at latest eval.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **31.43** | ✅ **Met** |
| AUROC > 0.75 | **0.86** | ✅ **Met** |
| ECE < 0.05 | **0.022** | ✅ **Met** |
| Diff loss → 4.0 | **4.21** | 🟡 Close |
| S1 accuracy → 40% | **27.7%** | ❌ **Lagging** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **Current v2 AR PPL superior** to v1 (31.4 vs 43.9). S1 performance **regression concern** - need 12pp improvement to hit 40% target.

## Infrastructure
**13 sessions, 12 spot reclaims** | Total cost: **$19.85** (vs $32.41 on-demand) | Current session: 2h uptime | Most reclaims at 11-13k steps (training instability correlation?)

## What's Next
**Training stable** through 30k. Monitor S1 accuracy recovery and diffusion loss convergence. After completion: comprehensive v2 benchmarks, confidence calibration analysis, investigate mid-training reclaim pattern.