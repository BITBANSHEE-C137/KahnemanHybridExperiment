# v3 Training SITREP

## v3 Training Status
**Step 45,200/50,000 (90.4%)** | GPU: 100% util, 82°C, 16.6GB/23GB VRAM | Rate: ~1.41 steps/sec | **ETA: 56min** | Spot: **$0.42/hr** (56.5% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 38000 | 28.43 | 4.02 | 28.5% | 0.864 | 0.0092 |
| 39000 | 28.34 | 4.04 | 29.0% | 0.863 | 0.0113 |
| 40000 | 28.27 | **3.76** | 30.3% | **0.881** | 0.0094 |
| 41000 | 28.30 | 3.95 | 27.8% | 0.866 | 0.0105 |
| 42000 | 28.33 | 3.89 | 29.1% | 0.870 | 0.0126 |
| 43000 | 28.14 | 4.20 | 25.9% | 0.869 | 0.0103 |
| 44000 | 28.07 | **4.40** | 24.9% | 0.867 | 0.0096 |
| 45000 | **27.95** | 4.16 | 26.5% | 0.870 | 0.0112 |

**Trends:** AR PPL steadily improving (-1.7% over 7k steps). Diff loss volatile, regressed from 3.76→4.16. S1 accuracy fluctuating, peaked at 30.3% then declined. AUROC stable ~0.87.

## Target Scorecard
| Target | Current | Met | Progress |
|--------|---------|-----|----------|
| AR PPL < 40 | **27.95** | ✅ | Excellent |
| AUROC > 0.75 | **0.870** | ✅ | Good |
| ECE < 0.05 | **0.0112** | ✅ | Excellent |
| Diff loss → 4.0 | **4.16** | ❌ | Close (4% over) |
| S1 accuracy → 40% | **26.5%** | ❌ | 66% of target |

**3/5 targets met.** Diffusion loss regression needs monitoring.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL
Current v3 AR PPL (**27.95**) outperforms both v1 (43.86) and GPT-2 (29.07).

## Infrastructure
**21 sessions, $36.21 total cost** | Current: g6.2xlarge us-east-1b, 9.1h uptime | Heavy spot interruptions 3/9-3/10 (10+ reclaims), stabilized since 3/11 | **$7.35 projected** vs $16.97 on-demand

## What's Next
5k steps to completion (~56min). Post-v3: benchmark suite (LAMBADA, WikiText-103), confidence calibration analysis, v1→v3 comparison study. Diffusion loss trajectory requires investigation.