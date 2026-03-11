# v3 Training SITREP

## v3 Training Status
**Step 45,400/50,000** (90.8%) • GPU: **100% util** L4 @ 73W/72W • **~4.6k steps remaining** (~20h ETA) • Spot: **$0.46/hr** (52.5% savings) • Current session: **0.9h uptime**

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

**Trends**: AR PPL steadily improving (-1.7% since 38k). **Diffusion loss volatile** (3.76→4.40). S1 accuracy **regressing** from 30.3% peak. AUROC stable ~0.87. ECE controlled <0.013.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.95** | ✅ **MET** |
| AUROC > 0.75 | **0.870** | ✅ **MET** |
| ECE < 0.05 | **0.011** | ✅ **MET** |
| Diff loss → 4.0 | **4.16** | 🟡 **Close** |
| S1 acc → 40% | **26.5%** | ❌ **Missing** |

## v1 Benchmark Baseline
v1@50k: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance superior to v1** (27.95 vs 43.86), S1 accuracy concerning vs v1's implied ~67% improvement.

## Infrastructure
**Total cost: $36.69** across 22 sessions. Current g6.2xlarge@us-east-1a stable 0.9h. **Heavy spot reclaim history** (20+ interruptions) - consider reserved capacity for final 4.6k steps. Most stable: 24h session cost $11.02.

## What's Next
Complete training in ~20h. **Critical**: Run v3 benchmarks immediately, compare S1 regression vs v1/v2, analyze confidence head calibration. Diffusion loss needs investigation - target 4.0 not consistently hit.