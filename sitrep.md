# v3 Training Status SITREP

## v3 Training Status
**JUST LAUNCHED** - Step 0/50k (0.0%). GPU idle, trainer initializing. A10G at 32°C, 2.2GB/23GB VRAM used. No rate/ETA available yet. Spot instance g5.2xlarge running at **$0.46/hr** (62% savings vs on-demand $1.21/hr).

## Eval Metrics & Trends
Latest trajectory data from step 43k-50k:

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43000 | 29.96 | 3.93 | 29.2% | 0.868 | 0.020 |
| 44000 | 29.96 | **4.37** | 25.4% | 0.865 | 0.016 |
| 45000 | 29.80 | 3.86 | 29.3% | 0.875 | 0.016 |
| 46000 | 29.74 | 4.15 | 26.2% | 0.865 | **0.011** |
| 47000 | 29.72 | **4.61** | 22.7% | 0.855 | 0.011 |
| 48000 | 29.72 | **4.73** | 21.9% | 0.858 | 0.012 |
| 49000 | **29.64** | 4.24 | 25.4% | 0.865 | **0.010** |
| 50000 | 29.65 | **4.70** | 22.0% | 0.863 | **0.009** |

**Trends**: AR PPL slowly improving (29.96→29.65). **Diffusion loss unstable**, oscillating 3.86-4.73. S1 accuracy volatile, trending down. AUROC stable ~0.86. **ECE improving** consistently (0.020→0.009).

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | 29.65 | ✅ **MET** |
| AUROC | > 0.75 | 0.863 | ✅ **MET** |
| ECE | < 0.05 | 0.009 | ✅ **MET** |
| Diff Loss | → 4.0 | 4.70 | ❌ **MISSING** |
| S1 Accuracy | → 40% | 22.0% | ❌ **MISSING** |

**3/5 targets met**. Diffusion loss and S1 accuracy significantly below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR PPL (**29.65**) substantially better than v1 (43.86). S1 performance (**22%** acc) concerning vs baseline expectations.

## Infrastructure
Single spot session active since 02:14 UTC (8.6 min uptime). **$0.044 total cost**. No spot reclaims. Instance stable in us-east-1a. Checkpoints through step 50k available, sync running.

## What's Next
Training just started - expect first metrics within hours. Monitor diffusion loss stability and S1 accuracy recovery. Current trajectory suggests AR performance excellent but **diffusion/S1 components need attention**. Will reassess targets after 5k steps.