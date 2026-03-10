# ML Ops SITREP - v3 Training Status

## v3 Training Status
**Step 34,800/50,000 (69.6%)** | GPU: **99% util**, L4 @ 70W/82°C, 16.6GB VRAM | Rate: ~5.2 steps/min | **ETA: 2.03 days** | Spot: **$0.46/hr** (53% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 27000 | 29.55  | 4.316     | 24.6%  | 0.866 | 0.0109 |
| 28000 | 29.40  | 4.513     | 23.8%  | 0.865 | 0.0068 |
| 29000 | 29.36  | 4.266     | 25.5%  | 0.867 | 0.0118 |
| 30000 | 29.16  | 4.337     | 24.6%  | 0.868 | 0.0046 |
| 31000 | 28.95  | 4.469     | 23.3%  | 0.871 | 0.0031 |
| 32000 | 29.04  | 4.350     | 24.2%  | 0.865 | 0.0089 |
| 33000 | 28.93  | 4.085     | 26.6%  | 0.861 | 0.0086 |
| 34000 | **28.85** | **4.149** | **25.6%** | **0.871** | **0.0069** |

**Trends:** AR PPL steadily improving (-2.4% over 7k steps). Diffusion loss volatile but trending down. S1 accuracy unstable around 25%. AUROC stable ~0.87. **ECE excellent** at 0.007.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.85** | ✅ **PASS** |
| AUROC > 0.75 | **0.871** | ✅ **PASS** |
| ECE < 0.05 | **0.007** | ✅ **PASS** |
| Diff loss → 4.0 | **4.15** | 🟡 **CLOSE** |
| S1 accuracy → 40% | **25.6%** | ❌ **MISS** |

**3/5 targets met.** S1 accuracy significantly behind target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 shows strong AR improvement** (28.85 vs 43.86 PPL), comparable diffusion performance.

## Infrastructure
Current: g6.2xlarge, 18.6h uptime, **19 total sessions** | **$28.52 total cost** | Multiple spot reclaims 3/9 (20+ interruptions), but recovery robust | Checkpoints: 32k/33k/34k available

## What's Next
Training stable, **15.2k steps remaining**. Post-completion: comprehensive v2 benchmarks, v1→v2 delta analysis, **confidence head deep-dive** (excellent ECE performance warrants investigation), S1 accuracy root cause analysis.