# v3 Training SITREP

## v3 Training Status
**Step 37,500/50,000 (75%)** | GPU: 100% util, 77°C | Rate: ~300 steps/hr | **ETA: 1.7 days**
Current spot: **$0.46/hr** (53% savings vs on-demand $0.98/hr) | Projected total: **$20.42**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 30000 | 29.16  | 4.34      | 24.6%  | 0.868 | 0.0046 |
| 33000 | 28.93  | **4.09**  | **26.6%** | 0.861 | 0.0086 |
| 35000 | 28.73  | 4.26      | 25.0%  | 0.863 | 0.0057 |
| 37000 | **28.51** | 4.52   | 24.1%  | 0.856 | **0.0065** |

**Trends:** AR PPL improving steadily. **Diff loss regressing** from 33k low. S1 accuracy volatile. AUROC slight decline. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.51** | ✅ **MET** |
| AUROC > 0.75 | **0.856** | ✅ **MET** |
| ECE < 0.05 | **0.0065** | ✅ **MET** |
| Diff loss → 4.0 | **4.52** | ❌ **REGRESSING** |
| S1 accuracy → 40% | **24.1%** | ❌ **STALLED** |

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 4.12 loss
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current v3 AR performance exceeds v1** (28.51 vs 43.86 PPL). S1 task showing resistance.

## Infrastructure
**19 spot sessions, 23h uptime** | Total cost: **$30.60** ($20.42 projected)
Current: g6.2xlarge, us-east-1a, stable 23h runtime
**Spot reliability: Good** - longest session 23.5h, no recent reclaims

## What's Next
**12.5k steps remaining** - monitor diff loss regression closely. If S1 accuracy doesn't improve by 40k, consider learning rate adjustment. Prepare v2 benchmark suite for comparison.