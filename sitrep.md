# v3 Training SITREP

## v3 Training Status
**Step 20,300/50,000 (40.6%)** | GPU: 100% util, 189W/300W, 54°C | **16.6GB/23GB VRAM**  
Rate: ~3.6 steps/min | **ETA: ~8.2 days** | Spot: $0.476/hr (**60.7% savings**)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 13000 | 28.41  | 4.42      | 24.1%  | 0.844 | 0.011  |
| 15000 | 28.64  | 4.50      | 23.7%  | **0.864** | 0.005  |
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008  |
| 19000 | 29.21  | 4.39      | 22.1%  | 0.866 | 0.011  |
| 20000 | **29.22** | 4.24   | **26.8%** | 0.857 | **0.005** |

**Trends:** AR PPL **degrading** (+0.8 over 7k steps). S1 accuracy **volatile** but recent uptick. Confidence calibration **excellent** (ECE ↓). AUROC stable ~0.86.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.22** | ✅ **MET** |
| AUROC | > 0.75 | **0.857** | ✅ **MET** |
| ECE | < 0.05 | **0.005** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.24** | 🟡 **CLOSE** |
| S1 Acc | → 40% | **26.8%** | ❌ **MISS** |

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR performance on-track vs v1, S1 accuracy lagging target.**

## Infrastructure
**5 sessions, 4 spot reclaims** | Total cost: **$15.17** (vs $45.71 on-demand)  
Current: g5.2xlarge, us-east-1b, 1h44m uptime  
Recent instability: 3 reclaims yesterday, now stable on current instance

## What's Next
**Concern:** S1 accuracy plateau at ~27% vs 40% target. Monitor AR PPL degradation trend.  
After v3: Full benchmark suite, confidence head analysis, v1-v3 comparison on held-out tasks.