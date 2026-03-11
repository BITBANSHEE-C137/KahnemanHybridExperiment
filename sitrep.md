# SITREP: v3 Training Progress

## v3 Training Status
**Step 44,300/50,000** (88.6% complete) | **GPU: 98% util** on L4 @ 82°C | **Rate:** ~7.6 steps/min | **ETA:** ~12.3 hrs | **Spot cost:** $0.43/hr (56.5% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|--------|--------|
| 37000 | 28.51  | 4.52      | 24.1%  | 0.856  | 0.0065 |
| 38000 | 28.43  | 4.02      | 28.5%  | 0.864  | 0.0092 |
| 39000 | 28.34  | 4.04      | 29.0%  | 0.863  | 0.0113 |
| 40000 | 28.27  | 3.76      | 30.3%  | 0.881  | 0.0094 |
| 41000 | 28.30  | 3.95      | 27.8%  | 0.866  | 0.0105 |
| 42000 | 28.33  | 3.89      | 29.1%  | 0.870  | 0.0126 |
| 43000 | 28.14  | 4.20      | 25.9%  | 0.869  | 0.0103 |
| **44000** | **28.07** | **4.40** | **24.9%** | **0.867** | **0.0096** |

**Key trends:** AR PPL gradually improving. **Diffusion loss regressed** from 3.76→4.40 (last 4k steps). S1 accuracy **volatile**, dropping from 30.3%→24.9%. AUROC stable ~0.87. ECE well-controlled.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **28.07** | ✅ **MET** |
| AUROC | > 0.75 | **0.867** | ✅ **MET** |
| ECE | < 0.05 | **0.0096** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.40** | ❌ **Regressing** |
| S1 Accuracy | → 40% | **24.9%** | ❌ **Far from target** |

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26% acc, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07
**Current v3 AR performance exceeds v1** (28.07 vs 43.86 PPL). S1 performance **needs major improvement** vs v1's effective 4.12 loss.

## Infrastructure
**Current session:** 7.6hrs uptime on g6.2xlarge spot @ $0.43/hr | **Total cost:** $35.61 across 21 sessions | **Major instability** March 9th (12 reclaims in 4hrs) | **Stable since March 10th** with only 2 longer sessions

## What's Next
**5,700 steps remaining** (~12hrs). **Critical:** Monitor diffusion loss regression and S1 accuracy volatility. Post-completion: v3 benchmarks, detailed v1→v3 comparison, confidence calibration analysis. **Diffusion head may need architectural review** if regression continues.