# v3 Training Status SITREP

## v3 Training Status
**TRAINING COMPLETE** ✅ Step **50,000/50,000** (100%)  
GPU: NVIDIA A10G idle (0% util, 11W power)  
Current instance: g5.2xlarge spot @ $0.48/hr (60.8% savings)  
Uptime: 4.8h, sync running, trainer stopped

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867 | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%  | 0.870 | 0.011 |
| 46000 | 28.13  | 3.94      | 28.1%  | 0.866 | 0.016 |
| 47000 | 28.09  | 3.88      | 29.3%  | 0.870 | 0.014 |
| 48000 | 28.04  | 4.19      | 26.1%  | 0.870 | 0.012 |
| 49000 | 28.05  | 4.41      | 24.9%  | 0.867 | 0.012 |
| 50000 | 27.99  | 4.16      | 26.5%  | 0.870 | 0.012 |

**Trends**: AR PPL stable ~28. **Diffusion loss volatile** (3.88→4.41). S1 accuracy oscillating 25-29%. AUROC/ECE stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **27.99** | ✅ |
| AUROC  | > 0.75 | **0.870** | ✅ |
| ECE    | < 0.05 | **0.012** | ✅ |
| Diff Loss | → 4.0 | **4.16** | ⚠️ |
| S1 Acc | → 40% | **26.5%** | ❌ |

**3/5 targets met**. Diffusion loss close but unstable. **S1 accuracy significantly below target**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07  

**v3 vs v1**: AR PPL improved (43.86→27.99), S1 accuracy regressed (41.2%→26.5%)

## Infrastructure
**23 sessions, $40.35 total cost** (60.9% spot savings vs $66.22 on-demand)  
Major reclaims: 15+ brief interruptions 3/9-3/10 (steps 19k-25k)  
Stable since 3/11: 3 clean handoffs, no data loss  
Current session: 4.8h uptime, no issues

## What's Next
**Training complete**. Execute v3 benchmarks: LAMBADA, WikiText-103, confidence calibration analysis. Compare v1→v3 progression. **Priority**: investigate S1 accuracy regression and diffusion loss instability.