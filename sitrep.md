# v2 Training SITREP

## v2 Training Status
**83% complete** - Step **41,500/50,000** on g5.2xlarge spot  
GPU: 100% util, 197W/300W, 50°C, 16.6GB VRAM used  
Rate: ~19 steps/min, **ETA: 7.4 hours**  
Current spot: **$0.46/hr** (62% savings), session cost: **$0.37**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 34000 | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 35000 | 30.84  | 4.79      | 21.4%  | 0.855 | 0.011 |
| 36000 | 30.69  | **4.30**  | 24.8%  | 0.863 | 0.010 |
| 37000 | 30.65  | 4.75      | 21.6%  | 0.861 | 0.007 |
| 38000 | 30.44  | **4.28**  | **26.7%** | 0.865 | **0.004** |
| 39000 | 30.41  | **3.80**  | **30.7%** | 0.863 | 0.007 |
| 40000 | 30.21  | 4.56      | 23.2%  | 0.857 | 0.007 |
| 41000 | **30.12** | 4.47   | 25.1%  | 0.862 | 0.012 |

**Trends:** AR PPL steadily improving. Diff loss volatile but trending down. S1 accuracy peaked at step 39k. AUROC stable ~0.86. ECE excellent.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.12** | ✅ **Met** |
| AUROC > 0.75 | **0.862** | ✅ **Met** |
| ECE < 0.05 | **0.012** | ✅ **Met** |
| Diff loss → 4.0 | **4.47** | 🔄 **Close** |
| S1 accuracy → 40% | **25.1%** | ❌ **Need +15%** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v2 AR performance significantly better than v1** (30.12 vs 43.86 PPL)

## Infrastructure
**15 spot sessions, 15 interruptions** - aggressive reclaiming  
Total cost: **$26.70** vs $85.20 on-demand (**69% savings**)  
Current session: 48min uptime, stable at $0.46/hr  
Pattern: Frequent 1-4hr interruptions, longest session 16hrs

## What's Next
**8.5k steps remaining** - complete by tomorrow morning  
Post-completion: v2 benchmarks vs v1/GPT-2, confidence calibration analysis  
**Key question:** Can S1 accuracy reach 40% in final 17%?