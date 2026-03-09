# v3 Training Status SITREP

## v3 Training Status
**Step 16,900/50,000** (33.8% complete) | A10G @ **98% util**, 197W/300W, 50°C | **62.3% spot savings** ($0.45/hr vs $1.21 on-demand) | ETA: ~4.5 days | Total cost: **$12.56** (projected $27.62)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 9000 | 26.95 | 5.06 | 18.4% | 0.805 | 0.006 |
| 12000 | 28.12 | 4.31 | 25.0% | 0.853 | 0.007 |
| 14000 | 28.51 | 4.29 | 24.7% | 0.852 | 0.009 |
| 16000 | **28.66** | **4.38** | **23.5%** | **0.856** | **0.010** |

**Trends**: AR PPL **regressing** (+1.7 since step 9k). Diffusion loss improved but **stalling** around 4.3-4.4. S1 accuracy peaked at 25% then **declined**. AUROC solid uptrend to 0.856. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.66** | ✅ |
| AUROC > 0.75 | **0.856** | ✅ |
| ECE < 0.05 | **0.010** | ✅ |
| Diff loss → 4.0 | **4.38** | ❌ (stalled) |
| S1 accuracy → 40% | **23.5%** | ❌ (declining) |

**3/5 targets met**. Concerning S1 regression and diffusion plateau.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v3 AR PPL (**28.66**) already **beating WikiText baseline** and approaching v1 performance. S1 loss correlates with accuracy regression.

## Infrastructure
**20.6h uptime** across 2 spot sessions. Session 1 terminated after 6.8h (steps 400-1000). Current session stable **20.6h**, no interruptions. VRAM: 16.2/23GB (70% util). Checkpoints syncing normally.

## What's Next
Address S1 accuracy decline - possible learning rate scheduling issue. Monitor diffusion loss convergence. Evaluate checkpoint at step 20k for potential intervention if S1 continues regressing.