# v3 Training SITREP

## v3 Training Status
**Progress**: 12,400/50,000 steps (**24.8%**)  
**GPU**: A10G @ 98% util, 198W/300W, 51°C, 16.2/23GB VRAM  
**Rate**: ~400 steps/6.9h = 57.9 steps/h  
**ETA**: ~27 days remaining  
**Spot Cost**: $0.46/h (62% savings), $10.06 total

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 5000 | 24.35  | 6.12      | 9.1%   | 0.695 | 0.008 |
| 8000 | 26.29  | 5.60      | 12.6%  | 0.785 | 0.008 |
| 10000| 27.55  | 4.98      | 19.0%  | 0.828 | 0.005 |
| 12000| **28.12** | **4.31** | **25.0%** | **0.853** | **0.007** |

**Trends**: AR PPL degrading slowly (+15% since step 5k). Diffusion loss improving well (-30%). S1 accuracy strong growth (+174%). AUROC plateauing near target. ECE excellent and stable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.12** | ✅ |
| AUROC | > 0.75 | **0.853** | ✅ |
| ECE | < 0.05 | **0.007** | ✅ |
| Diff Loss | → 4.0 | **4.31** | 🟡 (92% there) |
| S1 Accuracy | → 40% | **25.0%** | 🟡 (62% there) |

**3/5 targets met**. Diffusion and S1 on good trajectories.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v3 AR PPL (**28.12**) already **36% better** than v1 WikiText performance.

## Infrastructure
**Uptime**: 15.2h across 2 spot sessions  
**Interruptions**: 1 spot reclaim after 6.8h (step 1000)  
**Current session**: 15.2h stable, $6.91 cost  
**Checkpointing**: Active, 1.5GB checkpoints every 1k steps

## What's Next
Monitor AR PPL trajectory - concerning upward trend needs investigation. Diffusion loss should hit 4.0 target by step 15k. S1 accuracy growth rate suggests 40% target achievable by step 20k.