# Training SITREP - v2 Dual-Process Model

## v2 Training Status
**Step 24,400/50,000 (48.8% complete)** | GPU: 100% util, 196W/300W, 47°C | VRAM: 16.6/23GB | Rate: ~13.8 steps/min | **ETA: ~31 hours** | Spot cost: **$0.45/hr (63% savings)** | Total: $16.72

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|---------|-----------|-------------|-------|-----|
| 17000 | 30.70 | 4.52 | 23.7% | 0.860 | 0.0074 |
| 18000 | 30.77 | **4.03** | **27.2%** | **0.869** | **0.0060** |
| 19000 | 30.81 | 4.31 | 24.5% | 0.860 | 0.0073 |
| 20000 | 30.92 | 4.75 | 21.3% | 0.851 | 0.0072 |
| 21000 | 30.88 | 4.85 | 20.7% | 0.851 | 0.0075 |
| 22000 | 30.95 | 4.19 | **27.5%** | 0.858 | 0.0096 |
| 23000 | 31.03 | **4.03** | **27.9%** | 0.864 | 0.0095 |
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | **0.0050** |

**Trends:** AR PPL stable ~31. Diffusion loss volatile but improving. S1 accuracy peaked at 27.9% (step 23k). AUROC steady ~0.86. **ECE improved significantly** to 0.005.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.98** | ✅ **MET** |
| AUROC | > 0.75 | **0.863** | ✅ **MET** |
| ECE | < 0.05 | **0.005** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.46** | 🔄 **CLOSE** |
| S1 Accuracy | → 40% | **24.3%** | ❌ **MISS** |

**3/5 targets met.** Diffusion loss trending toward 4.0. S1 accuracy needs **+16pp** improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **Current v2 AR PPL (30.98) significantly better than v1 WikiText (43.86)** - joint training regression resolved.

## Infrastructure
**12 spot sessions, 11 reclaims.** Current: g5.2xlarge, us-east-1a, 38min uptime. **Aggressive spot reclaiming pattern** - longest session 10h. Cost efficiency: **$16.72 vs $38.17 on-demand**. Checkpoints syncing, trainer stable.

## What's Next
Training **51% remaining** (~31h). Monitor S1 accuracy plateau. Post-completion: v2 benchmarks, v1→v2 performance delta analysis, confidence calibration deep-dive.