# v3 Training SITREP

## v3 Training Status
**FRESH START** - Step **0/50k** (0.0%). GPU util 40% (A10G), power 112W/300W, temp 34°C. VRAM 4.4/23GB used. No active training rate yet. **61.7% savings** on spot @ $0.46/hr vs $1.21/hr on-demand.

## Eval Metrics & Trends
Using v2 final trajectory data (steps 43k-50k):

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 29.96  | 3.93      | 29.2%  | 0.868 | 0.020 |
| 44000 | 29.96  | 4.37      | 25.4%  | 0.865 | 0.016 |
| 45000 | 29.80  | 3.86      | 29.3%  | 0.875 | 0.016 |
| 46000 | 29.74  | 4.15      | 26.2%  | 0.865 | 0.011 |
| 47000 | 29.72  | 4.61      | 22.7%  | 0.855 | 0.011 |
| 48000 | 29.72  | 4.73      | 21.9%  | 0.858 | 0.012 |
| 49000 | 29.64  | 4.24      | 25.4%  | 0.865 | 0.010 |
| 50000 | 29.65  | 4.70      | 22.0%  | 0.863 | 0.009 |

**Trends**: AR PPL stable ~29.7. Diffusion loss volatile (3.86-4.73). S1 accuracy declining trend (29.2% → 22.0%). AUROC steady ~0.86. ECE improving (0.020 → 0.009).

## Target Scorecard
| Target | Current | Met |
|--------|---------|-----|
| AR PPL < 40 | **29.65** | ✅ |
| AUROC > 0.75 | **0.863** | ✅ |
| ECE < 0.05 | **0.009** | ✅ |
| Diff loss → 4.0 | **4.70** | ❌ |
| S1 accuracy → 40% | **22.0%** | ❌ |

**3/5 targets met**. Diffusion loss unstable, S1 accuracy significantly below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (29.65) beats v1 (43.86) by 32%**.

## Infrastructure
**3 spot reclaims** in <1 hour. Session history: 9min ($0.070), 8min ($0.064), current 8min ($0.048). Total cost **$0.18**. **Unstable spot availability** in us-east-1a causing frequent interruptions.

## What's Next
v3 just started - need to establish training rate and first eval checkpoint. Once stable: compare v3 early metrics to v2 trajectory, analyze S1 accuracy regression, consider diffusion loss regularization.