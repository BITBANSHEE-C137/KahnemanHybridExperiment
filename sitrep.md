# v2 Training SITREP

## v2 Training Status
**Step 36,500/50,000 (73%)** | A10G @ **99% util**, 188W/300W, 50°C | **~1.1k steps/day** | ETA: **~12 days** | Spot: **$0.45/hr** (-63% vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 29000 | 31.43  | 4.21      | 27.7%  | 0.860 | 0.022 |
| 30000 | 31.68  | 4.08      | 28.1%  | 0.864 | 0.023 |
| 31000 | 31.60  | 4.49      | 24.5%  | 0.862 | 0.014 |
| 32000 | 31.39  | 3.96      | 28.4%  | 0.871 | 0.013 |
| 33000 | 31.29  | 4.23      | 25.4%  | 0.864 | 0.008 |
| 34000 | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 35000 | 30.84  | 4.79      | 21.4%  | 0.855 | 0.011 |
| **36000** | **30.69** | **4.30** | **24.8%** | **0.863** | **0.010** |

**Trends:** AR PPL steadily improving ✅. Diffusion loss volatile, trending up ⚠️. S1 accuracy erratic, recent uptick. AUROC stable ~0.86. ECE excellent <0.02.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **30.69** | ✅ |
| AUROC  | > 0.75 | **0.863** | ✅ |
| ECE    | < 0.05 | **0.010** | ✅ |
| Diff Loss | → 4.0 | **4.30** | ⚠️ |
| S1 Acc | → 40%  | **24.8%** | ❌ |

**3/5 targets met.** S1 accuracy significantly behind target. Diffusion loss needs 7% improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 AR already outperforming v1** (30.69 vs 43.86 PPL). Diffusion loss regression from joint training expected.

## Infrastructure
**13 spot sessions, 23.7k total steps.** Current session: 10.4hr uptime, **$4.72 cost**. Total project cost: **$23.70** (63% savings vs on-demand). No recent interruptions - stable us-east-1b performance.

## What's Next
v2 completion in ~12 days. **Priority:** Monitor diffusion loss volatility and S1 accuracy plateau. Post-completion: full benchmark suite, v1/v2 head-to-head comparison, confidence calibration deep-dive on ECE excellence.