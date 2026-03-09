# v3 Training SITREP

## v3 Training Status
**Step 18,600 / 50,000** (37.2% complete)  
GPU: A10G @ **100% util**, 209W/300W, 51°C, 16.2GB/23GB VRAM  
Rate: ~400 steps/day, **ETA: ~79 days**  
Spot cost: **$0.454/hr** (62% savings), projected total: **$27.59**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|---------|-----------|--------|-------|-------|
| 11000 | 27.85   | 4.43      | 21.97% | 0.853 | 0.010 |
| 12000 | 28.12   | 4.31      | 25.03% | 0.853 | 0.007 |
| 13000 | 28.41   | 4.42      | 24.13% | 0.844 | 0.011 |
| 14000 | 28.51   | 4.29      | 24.68% | 0.852 | 0.009 |
| 15000 | 28.64   | 4.50      | 23.75% | 0.864 | 0.005 |
| 16000 | 28.66   | 4.38      | 23.53% | 0.856 | 0.010 |
| 17000 | 28.89   | 4.34      | 25.22% | 0.858 | 0.008 |
| 18000 | **28.99** | **4.44**  | **22.97%** | **0.858** | **0.010** |

**Trends:** AR PPL slowly degrading (+1.1 over 7k steps). Diffusion loss oscillating around 4.4. S1 accuracy volatile, no clear trend. AUROC stable ~0.85. **⚠️ All metrics stagnating/regressing.**

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.99** | ✅ |
| AUROC > 0.75 | **0.858** | ✅ |
| ECE < 0.05 | **0.010** | ✅ |
| Diff loss → 4.0 | **4.44** | ❌ (+10% above) |
| S1 accuracy → 40% | **22.97%** | ❌ (-43% below) |

**2/5 targets met.** S1 performance severely lagging expectations.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, PPL 1.46; WikiText-103 PPL 43.86; S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (28.99) beats both baselines.** S1 diffusion loss comparable to v1.

## Infrastructure
**Current session:** 22.6hrs uptime, $10.35 spot cost  
**Previous session:** 6.7hrs, $3.11 (spot reclaimed)  
**Total:** 2 sessions, $13.43 spent, **87% uptime**  
Checkpoints syncing, trainer stable.

## What's Next
**Major concern:** S1 accuracy plateau at ~23% vs 40% target. Consider learning rate adjustment or architecture changes. Current trajectory suggests targets won't be met by step 50k.