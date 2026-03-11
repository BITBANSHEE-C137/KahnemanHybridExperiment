# v3 Training SITREP

## v3 Training Status
**Step 36,600/50,000 (73.2%)** | GPU: **100% util** L4 @ 83°C | Rate: ~6.2 steps/min | **ETA: 36hrs** | Spot: **$0.46/hr** (53% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 29k  | 29.36  | 4.27     | 25.5%   | 0.867  | 0.012 |
| 30k  | 29.16  | 4.34     | 24.6%   | 0.868  | 0.005 |
| 31k  | 28.95  | 4.47     | 23.3%   | 0.871  | 0.003 |
| 32k  | 29.04  | 4.35     | 24.2%   | 0.865  | 0.009 |
| 33k  | 28.93  | 4.09     | 26.6%   | 0.861  | 0.009 |
| 34k  | 28.85  | 4.15     | 25.6%   | 0.871  | 0.007 |
| 35k  | 28.73  | 4.26     | 25.0%   | 0.863  | 0.006 |
| 36k  | **28.59** | **4.46** | **23.5%** | **0.864** | **0.011** |

**Trends:** AR PPL improving steadily (-2.7% over 7k steps). S1 accuracy volatile, currently regressing. Diffusion loss unstable around 4.3±0.15. AUROC plateau ~0.86. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.59** | ✅ **BEAT** |
| AUROC > 0.75 | **0.864** | ✅ **BEAT** |
| ECE < 0.05 | **0.011** | ✅ **BEAT** |
| Diff loss → 4.0 | **4.46** | ❌ Miss by 0.46 |
| S1 accuracy → 40% | **23.5%** | ❌ Miss by 16.5pp |

**3/5 targets met.** S1 accuracy severely underperforming (41% below target). Diffusion loss needs 10% improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. **v3 AR already 35% better than v1 WikiText PPL** (28.6 vs 43.9). Current diffusion loss 4.46 vs v1's 4.12 - slight regression but marginal.

## Infrastructure
**19 sessions, $29.90 total cost.** Current g6.2xlarge stable **21.5hrs** uptime. Heavy spot churn Mar 9 (12 reclaims in 4hrs) cost $1.65 in restarts. Switched to us-east-1a for stability. Last checkpoint: step_36000.pt (1.5GB, synced).

## What's Next
**13,400 steps remaining (~36hrs).** Focus: S1 head analysis - accuracy plateau suggests architectural bottleneck or training instability. Post-completion: comprehensive v1 vs v3 benchmarks, confidence calibration deep-dive.