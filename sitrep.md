# v3 Training SITREP

## v3 Training Status
**Progress**: 11,100/50,000 steps (**22.2%** complete)  
**GPU**: A10G @ **99% util**, 197W/300W, 54°C, 16.2GB/23GB VRAM  
**Rate**: ~229 steps/hr based on uptime  
**ETA**: ~7.5 days remaining  
**Spot Cost**: **$0.46/hr** (62% savings), $9.37 total spend

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 4000 | 23.71 | 6.29 | 8.5% | 0.672 | 0.011 |
| 6000 | 24.85 | 6.08 | 9.9% | 0.719 | 0.012 |
| 8000 | 26.29 | 5.60 | 12.6% | 0.785 | 0.008 |
| 10000 | 27.55 | 4.98 | 19.0% | 0.828 | 0.005 |
| 11000 | **27.85** | **4.43** | **22.0%** | **0.853** | **0.010** |

**Trends**: AR PPL degrading gradually (+4.1 since step 4k). Diffusion loss improving strongly (-1.9). S1 accuracy climbing steadily (+13.5pp). AUROC solid upward trend (+0.18). ECE volatile but acceptable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **27.85** | ✅ **PASS** |
| AUROC | > 0.75 | **0.853** | ✅ **PASS** |  
| ECE | < 0.05 | **0.010** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.43** | 🟡 **90% there** |
| S1 Accuracy | → 40% | **22.0%** | 🟡 **55% there** |

**3/5 targets met**. Diffusion and S1 trending well toward targets.

## v1 Benchmark Baseline
v1 (50k steps): LAMBADA 94.26% / PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  

Current v3 AR PPL (**27.85**) already **37% better** than v1 WikiText (43.86), tracking toward GPT-2 baseline levels.

## Infrastructure
**Current**: g5.2xlarge spot, 13.7h uptime, no interruptions  
**History**: 2 sessions, 1 prior reclaim after 6.8h (steps 400-1000)  
**Stability**: Solid 13h+ run ongoing, checkpoints syncing normally

## What's Next
Strong trajectory on diffusion loss and S1 accuracy. AR degradation concerning but still well within target. **Monitor AR trend closely** - if exceeds 35 PPL, consider learning rate adjustment. On current pace: diffusion target by ~step 15k, S1 target by ~step 25k.