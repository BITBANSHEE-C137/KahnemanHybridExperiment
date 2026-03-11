# v3 Training SITREP

## v3 Training Status
**Step 45,100/50,000 (90.2% complete)**  
GPU: **99.0%** util, NVIDIA L4 @ 80°C, 16.6/23GB VRAM  
Rate: ~27 min remaining based on trajectory  
Spot: **$0.46/hr** (52.4% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 38000 | 28.43  | 4.02      | 28.5%  | 0.864 | 0.009 |
| 39000 | 28.34  | 4.04      | 29.0%  | 0.863 | 0.011 |
| 40000 | 28.27  | **3.76**  | 30.3%  | **0.881** | 0.009 |
| 41000 | 28.30  | 3.95      | 27.8%  | 0.866 | 0.011 |
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870 | 0.013 |
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869 | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%  | 0.867 | 0.010 |
| 45000 | **27.95** | 4.16   | 26.5%  | 0.870 | 0.011 |

**Trends**: AR PPL steadily improving (**-0.5 over 7k steps**). Diff loss **volatile** around 4.0. S1 accuracy **stagnant** ~28%. AUROC stable ~0.87, ECE well-controlled <0.015.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | <40 | **27.95** | ✅ **BEAT** |
| AUROC | >0.75 | **0.870** | ✅ **BEAT** |
| ECE | <0.05 | **0.011** | ✅ **BEAT** |
| Diff Loss | →4.0 | **4.16** | ⚠️ **CLOSE** |
| S1 Acc | →40% | **26.5%** | ❌ **MISS** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (27.95) beats v1 WikiText baseline** - joint training not regressing AR performance.

## Infrastructure
**22 spot sessions**, total cost **$36.45**  
Current: g6.2xlarge us-east-1a, 27min uptime  
Recent stability: 9hr session (40k-45k steps) before reclaim  
**Reclaim pattern**: Frequent 1-4hr interruptions, suggest multi-AZ strategy

## What's Next
**5k steps to completion** (~3-4 hours at current rate)  
Post-completion: v3 benchmarks vs v1 baseline, S1 token accuracy deep-dive (concerning plateau), confidence calibration analysis on final checkpoints