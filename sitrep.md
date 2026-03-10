# v3 Training SITREP

## v3 Training Status
- **Step 24,200/50,000** (48.4% complete)
- GPU: **100% utilization** on L4, 72W power, 81°C, 16.6GB VRAM used
- Rate: ~400 steps per session (variable due to spot interruptions)
- ETA: **~26k more steps** (~65 hours at current rate)
- Spot cost: **$0.45/hr** (53.5% savings vs on-demand $0.98/hr)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008  |
| 18000 | 28.99  | 4.44      | 23.0%  | 0.858 | 0.010  |
| 19000 | 29.21  | 4.39      | 22.1%  | 0.866 | 0.011  |
| 20000 | 29.22  | 4.24      | 26.8%  | 0.857 | 0.005  |
| 21000 | 29.94  | 4.26      | 26.8%  | 0.856 | 0.012  |
| 22000 | 29.70  | **3.95**  | 28.3%  | **0.876** | **0.004** |
| 23000 | 29.57  | 4.19      | 26.1%  | 0.861 | 0.006  |
| 24000 | 29.53  | 4.31      | 25.2%  | 0.862 | 0.005  |

**Trends:** AR PPL plateaued ~29. Diffusion loss hit **3.95 at step 22k** (best so far) but regressed. AUROC peaked at **0.876**. S1 accuracy volatile but trending up slightly.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.5** | ✅ **Met** |
| AUROC > 0.75 | **0.862** | ✅ **Met** |
| ECE < 0.05 | **0.005** | ✅ **Met** |
| Diff loss → 4.0 | **4.31** | ❌ Need 0.31↓ |
| S1 accuracy → 40% | **25.2%** | ❌ Need 14.8%↑ |

**3/5 targets met.** Diffusion loss tantalizingly close after hitting 3.95.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR PPL (29.5) matches GPT-2 baseline**, suggesting minimal AR degradation from joint training.

## Infrastructure
- **19 spot sessions** across g5/g6 instances, **$20.30 total cost**
- Current: g6.2xlarge, us-east-1a, running 34min (stable)
- Previous session: 6h runtime before spot reclaim
- **Major instability Mar 9 17:00-22:00**: 8 spot reclaims in 5 hours
- Cost efficiency: **53.5% savings** vs on-demand

## What's Next
- Monitor diffusion loss - need sustained <4.0 breakthrough
- S1 accuracy remains stubborn - investigate confidence head dynamics
- After v3: comprehensive v1/v2/v3 benchmark comparison, confidence calibration analysis
- Consider instance type optimization to reduce spot volatility