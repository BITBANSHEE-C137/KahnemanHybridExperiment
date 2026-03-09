# ML Ops SITREP - v3 Training

## v3 Training Status
**TRAINING HALTED** - Step 0/50k (0%). Last checkpoint: step 20k (Mar 9 16:07 UTC).
- GPU: A10G @ 99% util, 206W/300W, 62°C, 16.6GB/23GB VRAM
- Current: g5.xlarge spot @ $0.45/hr (55% savings vs on-demand)
- **Issue**: Training stuck at step 0 despite 20k checkpoint available

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|--------|-----|
| 13k  | 28.41  | 4.42      | 24.1%   | 0.844  | 0.011 |
| 15k  | 28.64  | 4.50      | 23.7%   | **0.864** | **0.005** |
| 17k  | 28.89  | 4.34      | 25.2%   | 0.858  | 0.008 |
| 20k  | 29.22  | 4.24      | **26.8%** | 0.857  | 0.005 |

**Trends**: AR PPL slowly degrading (+0.8 over 7k steps). Confidence calibration excellent (ECE < 0.01). S1 accuracy volatile but trending up. AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | 29.22   | ✅ |
| AUROC  | > 0.75 | 0.857   | ✅ |
| ECE    | < 0.05 | 0.005   | ✅ |
| Diff Loss | → 4.0 | 4.24   | 🟡 Close |
| S1 Acc | → 40% | 26.8%   | ❌ Gap |

**3/5 targets met**. S1 accuracy 13.2pp below target. Diffusion loss 0.24 above target.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26% (PPL 1.46), WikiText-103 PPL 43.86, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07
- Current AR PPL (29.22) **significantly better** than v1 final (43.86)
- On track to match pretrained baseline performance

## Infrastructure
**Spot carnage**: 15 sessions, 12 interruptions since Mar 8. Total cost: **$16.33**.
- Heavy churn: 7 interruptions yesterday alone (18:00-20:00 UTC)
- Instance hopping: g5.xlarge→g6.xlarge→g5.2xlarge (rate shopping)
- Current uptime: 10min (just rebooted)

## What's Next
**CRITICAL**: Debug training restart from step 20k checkpoint. Trainer process running but stuck.
Post-recovery: Resume to 50k, then full v2 benchmark suite vs v1 baseline. Focus on S1 accuracy gap analysis.