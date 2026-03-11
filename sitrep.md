# v3 Training SITREP

## v3 Training Status
**FRESH RESTART** - Current step: **0/50k** (0.0%)  
GPU: L4 @ 100% util, 72W/72W limit, 53°C, 16.5GB/23GB VRAM  
Rate: TBD (just booted 8min ago)  
ETA: TBD  
Spot: **$0.43/hr** (56% savings vs $0.98 on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 33000 | 28.93 | 4.085 | 26.6% | 0.861 | 0.009 |
| 34000 | 28.85 | 4.149 | 25.6% | **0.871** | 0.007 |
| 35000 | 28.73 | 4.259 | 25.0% | 0.863 | 0.006 |
| 36000 | 28.59 | **4.463** | 23.5% | 0.864 | **0.011** |
| 37000 | 28.51 | 4.524 | 24.1% | 0.856 | 0.006 |
| 38000 | 28.43 | 4.022 | **28.5%** | 0.864 | 0.009 |
| 39000 | 28.34 | 4.043 | 29.0% | 0.863 | **0.011** |
| 40000 | **28.27** | **3.757** | **30.3%** | **0.881** | 0.009 |

**Trends:** AR PPL steadily improving ✓ Diff loss volatile but trending down ✓ S1 accuracy recovering strongly ✓ AUROC solid ✓ ECE stable ✓

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.27** | ✅ **MET** |
| AUROC | > 0.75 | **0.881** | ✅ **MET** |
| ECE | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **3.757** | ✅ **MET** |
| S1 Accuracy | → 40% | **30.3%** | ❌ **Need +9.7pp** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 already beats v1 AR performance** (28.27 vs 43.86 PPL)

## Infrastructure
**21 spot sessions, $32.42 total cost** - chronic instability  
Current: g6.2xlarge, us-east-1b, 8min uptime  
Previous session: 3hr run (steps 38k→40.3k) before termination  
**Major issue:** Training restarted at step 0 despite checkpoints available

## What's Next
**CRITICAL:** Investigate checkpoint loading failure - should resume from step 40k, not restart  
Once fixed: push to 50k steps, then v2 benchmarks and confidence analysis  
Current trajectory suggests **strong performance** if training stability improves