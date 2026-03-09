# v3 Training SITREP

## v3 Training Status
**Step 20,100/50,000 (40.2%)** | A10G @ 100% util, 195W/300W, 51°C | **16.6GB/23GB VRAM** | Current rate ~2.5 steps/min | **ETA: ~8 days** | Spot: **$0.44/hr (56% savings)** | Total cost: **$17.01**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|--------|-------|-----|
| 13000 | 28.41 | 4.42 | 24.1% | 0.844 | 0.011 |
| 15000 | 28.64 | 4.50 | 23.7% | **0.864** | **0.005** |
| 17000 | 28.89 | 4.34 | **25.2%** | 0.858 | 0.008 |
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.011 |
| 20000 | **29.22** | **4.24** | **26.8%** | 0.857 | **0.005** |

**Trends**: AR PPL degrading (+0.8 from step 13k). Diffusion loss volatile but improving. S1 accuracy noisy but trending up. AUROC stable ~0.86. ECE excellent, meeting target.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **29.22** | ✅ |
| AUROC | > 0.75 | **0.857** | ✅ |
| ECE | < 0.05 | **0.005** | ✅ |
| Diff Loss | → 4.0 | **4.24** | 🟡 (improving) |
| S1 Accuracy | → 40% | **26.8%** | 🔴 (progressing) |

**3/5 targets met**. AR performance solid. Confidence calibration excellent. S1 accuracy and diffusion loss need improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 4.12 loss. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR PPL (29.22) significantly better than v1 (43.86)** but still behind GPT-2. S1 performance lagging v1's 67% improvement.

## Infrastructure
**17 spot sessions, 9 reclaims in last 4 hours** - extreme instability. Burned through g5.xlarge → g6.xlarge → g5.2xlarge → g6.2xlarge. Current session: 17min uptime. **Total cost $16.98 across all sessions**. Spot market chaos causing training inefficiency.

## What's Next
**Critical**: Stabilize infrastructure - consider reserved instances or higher bid prices. Current reclaim rate unsustainable. After stabilization: push S1 accuracy toward 40%, continue diffusion loss reduction to 4.0. Monitor AR PPL regression - may need learning rate adjustment.