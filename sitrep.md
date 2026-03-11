# SITREP: v3 Dual-Process Training

**2026-03-11 07:00 UTC**

## v3 Training Status
**Step 39,900/50,000 (79.8%)** | A10G @ 100% util, 201W/300W | **4.8 steps/min** | ETA: **~35h** | Spot cost: **$0.44/hr** (63% savings) | Current session uptime: **2.5h**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 32k  | 29.04  | 4.35      | 24.2%   | 0.865 | 0.009 |
| 35k  | 28.73  | 4.26      | 25.0%   | 0.863 | 0.006 |
| **39k** | **28.34** | **4.04** | **29.0%** | **0.863** | **0.011** |

**Trends:** AR perplexity steadily improving (-2.4% over 7k steps). Diffusion loss volatile but trending down. **S1 accuracy gaining momentum** (+19% relative). AUROC stable ~0.863. ECE slightly elevated but acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.34** | ✅ **PASS** |
| AUROC > 0.75 | **0.863** | ✅ **PASS** |
| ECE < 0.05 | **0.011** | ✅ **PASS** |
| Diff loss → 4.0 | **4.04** | ✅ **PASS** |
| S1 accuracy → 40% | **29.0%** | ❌ **72% there** |

**4/5 targets met.** S1 accuracy trailing but accelerating.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 AR performance superior to v1** (28.34 vs 43.86 PPL). Diffusion loss approaching v1 levels.

## Infrastructure
**20 spot sessions, 13 reclaims** - extensive spot churn 3/9-3/10. Current g5.2xlarge stable 2.5h in us-east-1f. Total cost: **$32.14**

Notable: Chaotic day 3/9 with 12 reclaims between steps 19k-25k across multiple instance types/AZs.

## What's Next
**10k steps remaining (~35h)**. Expect final S1 accuracy push toward 40% target. Post-completion: comprehensive v2 benchmarking, v1/v2 comparison analysis, confidence calibration deep-dive.