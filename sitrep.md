# v2 Training SITREP

## v2 Training Status
**Step 22,500/50,000 (45% complete)**
- GPU: 100% util, A10G @ 194W/300W, 55°C, 16.6/23GB VRAM
- Rate: ~3.4 steps/min based on current session
- **ETA: ~13.5 hours** to completion
- Spot cost: **$0.45/hr** (63% savings vs $1.21 on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 15000| 31.05  | 4.33      | 26.1%  | 0.852 | 0.014 |
| 16000| 30.79  | 4.13      | 26.8%  | 0.860 | 0.007 |
| 17000| 30.70  | 4.52      | 23.7%  | 0.860 | 0.007 |
| 18000| 30.77  | 4.03      | 27.2%  | 0.869 | 0.006 |
| 19000| 30.81  | 4.31      | 24.5%  | 0.860 | 0.007 |
| 20000| 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 21000| 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000| **30.95** | **4.19** | **27.5%** | **0.858** | **0.010** |

**Trends**: AR PPL stagnating ~31, diff loss volatile (4.0-4.9). **S1 accuracy recovery** from 20.7%→27.5% last 1k steps. AUROC stable mid-0.85s.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.95** | ✅ **MET** |
| AUROC > 0.75 | **0.858** | ✅ **MET** |
| ECE < 0.05 | **0.010** | ✅ **MET** |
| Diff loss → 4.0 | **4.19** | 🔄 Close (4.0-4.9 range) |
| S1 accuracy → 40% | **27.5%** | ❌ **12.5% gap** |

**3/5 targets met**. S1 accuracy most concerning - needs 45% improvement.

## v1 Benchmark Baseline
v1 @ 50k: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v2 **AR PPL 30.95 significantly better than v1's 43.86** - joint training improving rather than regressing. S1 performance gap remains (27.5% vs target 40%).

## Infrastructure
**11 spot sessions**, 10 reclaims over 2 days. **$15.58 total cost** vs $43.70 on-demand.
- Current session: 2.8hrs uptime, stable
- Recent volatility in us-east-1 spot market
- Instance type mixing (g5.xlarge fallbacks during shortages)

## What's Next
- **ETA completion**: Tomorrow morning ~07:30 UTC
- Post-training: v2 benchmarks on LAMBADA/WikiText
- **Critical**: Compare S1 token accuracy vs v1 final metrics
- Confidence head calibration analysis on held-out data