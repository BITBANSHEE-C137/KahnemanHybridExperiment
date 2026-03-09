## v3 Training Status
**Step 20,100/50,000 (40.2% complete)** - NVIDIA L4 @ 100% util, 72W/75°C. **No recent eval data available**. Current spot rate $0.43/hr (56.5% savings). ETA ~30k more steps.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |
| 15000 | 28.64 | 4.50 | 23.7% | 0.864 | 0.005 |
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.008 |
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.011 |
| 20000 | 29.22 | 4.24 | 26.8% | 0.857 | 0.005 |

**Concerning trends:** AR PPL gradually degrading (+0.8 since step 13k). S1 accuracy volatile but improved at step 20k. AUROC stable ~0.86, ECE excellent <0.01.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.22** | ✅ |
| AUROC > 0.75 | **0.857** | ✅ |
| ECE < 0.05 | **0.005** | ✅ |
| Diff loss → 4.0 | **4.24** | 🔄 |
| S1 accuracy → 40% | **26.8%** | ❌ |

**3/5 targets met.** S1 accuracy significantly behind target. Diffusion loss trending down but needs more progress.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. Current v3 AR performance (**PPL 29.22**) approaching GPT-2 baseline, major improvement over v1's WikiText performance.

## Infrastructure
**16 spot reclaims in 3 days** - excessive instability. Multiple brief sessions <1hr indicate aggressive spot terminations. Currently on g6.2xlarge @ $0.43/hr. Total cost: **$16.78**. 27min uptime on current instance.

**Critical:** Spot market extremely volatile, hampering training efficiency.

## What's Next
Need eval checkpoint urgently - last eval at step 20k. Focus on S1 accuracy improvements and diffusion loss convergence. Consider reserved capacity given spot instability.