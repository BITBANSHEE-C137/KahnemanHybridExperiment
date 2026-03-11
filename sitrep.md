# v3 Training SITREP - Step 35,400

## v3 Training Status
**Progress**: 35,400/50,000 steps (**70.8%** complete)  
**GPU**: L4 @ **99%** utilization, 72W limit, 82°C, 16.6/23GB VRAM  
**Rate**: ~1.5 steps/min | **ETA**: ~10 days  
**Current Cost**: $8.98 spot ($29.02 total) | **53.1% savings** vs on-demand

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|--------|-------|
| 28000 | 29.40  | 4.51      | 23.8%  | 0.865  | 0.007 |
| 29000 | 29.36  | 4.27      | 25.5%  | 0.867  | 0.012 |
| 30000 | 29.16  | 4.34      | 24.6%  | 0.868  | 0.005 |
| 31000 | 28.95  | 4.47      | 23.3%  | 0.871  | 0.003 |
| 32000 | 29.04  | 4.35      | 24.2%  | 0.865  | 0.009 |
| 33000 | 28.93  | 4.09      | 26.6%  | 0.861  | 0.009 |
| 34000 | 28.85  | 4.15      | 25.6%  | 0.871  | 0.007 |
| **35000** | **28.73** | **4.26** | **25.0%** | **0.863** | **0.006** |

**Trends**: AR perplexity steadily improving (-0.67 from 28k). Diffusion loss volatile but trending down. S1 accuracy fluctuating 23-27%. AUROC stable ~0.86. ECE well-controlled <0.012.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.73** | ✅ **BEAT** |
| AUROC > 0.75 | **0.863** | ✅ **BEAT** |
| ECE < 0.05 | **0.006** | ✅ **BEAT** |
| Diff Loss → 4.0 | **4.26** | ⚠️ Close |
| S1 Acc → 40% | **25.0%** | ❌ **Need +15pp** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3**: AR significantly better than v1 (28.73 vs 43.86), S1 accuracy lagging badly.

## Infrastructure
**Current**: g6.2xlarge (L4) @ $0.46/hr spot, **19h 35m** uptime  
**History**: **19 sessions**, frequent spot reclaims Mar 9 (8 interruptions in 4 hours)  
**Stability**: Current session stable for 19+ hours, sync/trainer running  
**Checkpoints**: Latest step_35000.pt (1.5GB), syncing active

## What's Next
**S1 token accuracy is critically low** - investigate training dynamics and loss weighting. Consider confidence head ablation study. Target completion ~Mar 21 if no more spot interruptions. Post-completion: comprehensive v1 vs v3 benchmark comparison focusing on the AR/S1 trade-off.