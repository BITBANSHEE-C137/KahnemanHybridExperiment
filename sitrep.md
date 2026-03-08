# v3 Training SITREP

## v3 Training Status
**CRITICAL: Training not started** - step 0/50k (0.0%). GPU at 61% util, low VRAM usage (2.1GB/23GB). A10G running cool at 31°C. Current spot rate $0.46/hr (62% savings vs on-demand). **ETA: Unknown - training stalled**.

## Eval Metrics & Trends
Using **v2 final trajectory** (steps 43k-50k) as reference:

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 29.96 | 3.93 | 29.2% | 0.868 | 0.020 |
| 44000 | 29.96 | **4.37** | **25.4%** | 0.865 | 0.016 |
| 47000 | 29.72 | **4.61** | **22.7%** | **0.855** | 0.011 |
| 50000 | **29.65** | **4.70** | **22.0%** | 0.863 | **0.009** |

**Trends**: AR PPL stabilized ~29.7. **Diffusion loss regressing** (3.93→4.70). **S1 accuracy declining** (29%→22%). AUROC volatile but stable ~0.86. ECE improving (0.020→0.009).

## Target Scorecard
| Metric | Target | v2 Final | Status |
|--------|--------|----------|--------|
| AR PPL | < 40 | **29.65** | ✅ **MET** |
| AUROC | > 0.75 | **0.863** | ✅ **MET** |
| ECE | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.70** | ❌ **REGRESSING** |
| S1 Accuracy | → 40% | **22.0%** | ❌ **FAR BELOW** |

**3/5 targets met**. Diffusion and S1 performance concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v2 AR PPL (29.65) matches GPT-2 baseline** - significant improvement from v1's 43.86.

## Infrastructure
**MAJOR INSTABILITY**: 5 spot reclaims in ~2 hours. Sessions averaging 8-9 minutes before termination. Total cost $0.32 across failed attempts. Current instance up 8 minutes - **expect imminent reclaim**. us-east-1a showing high contention.

## What's Next
**IMMEDIATE**: Investigate v3 training initialization failure. Consider switching AZ or instance type. **After restart**: Complete v3 training with focus on diffusion loss stabilization and S1 accuracy recovery. v2 shows promising AR convergence but dual-process balance needs work.