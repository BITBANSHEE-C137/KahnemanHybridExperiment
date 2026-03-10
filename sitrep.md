# v3 Training SITREP

## v3 Training Status
**Step 22,900/50,000** (45.8% complete). A10G at **100% utilization**, 195W/300W power. Current rate: ~1.8 steps/min. **ETA: ~17 days**. Spot cost: **$0.48/hr** (60.7% savings vs on-demand). Current session: 3.7h uptime, $1.76 spent.

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 15000 | 28.64 | 4.50 | 23.7% | 0.864 | 0.0052 |
| 17000 | 28.89 | 4.34 | 25.2% | 0.858 | 0.0079 |
| 19000 | 29.21 | 4.39 | 22.1% | 0.866 | 0.0106 |
| 21000 | 29.94 | 4.26 | 26.8% | 0.856 | 0.0116 |
| **22000** | **29.70** | **3.95** | **28.3%** | **0.876** | **0.0039** |

**Trends:** AR PPL stagnant around 29. **Diffusion loss dropped significantly** from 4.3→3.95 (breakthrough). S1 accuracy climbing steadily. AUROC **improved strongly** to 0.876. ECE volatile but currently excellent.

## Target Scorecard
- ✅ **ECE < 0.05**: 0.0039 (EXCEEDED)
- ✅ **AUROC > 0.75**: 0.876 (STRONG)
- ❌ **AR PPL < 40**: 29.7 (beating target but not improving)
- ❌ **Diff loss → 4.0**: 3.95 (VERY CLOSE, trending down)
- ❌ **S1 accuracy → 40%**: 28.3% (climbing, +5.9% since step 15k)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. Current v3 AR PPL **32% better** than v1 WikiText. Diffusion loss nearly matching v1 S1 performance. Joint training showing **no AR regression** vs v1.

## Infrastructure
**18 spot sessions**, frequent reclaims causing training instability. Multiple failed G6 attempts. Current g5.2xlarge stable for 3.7h. **Total cost: $18.88** across all sessions. Cost efficiency: **$0.83/1000 steps**.

## What's Next
Monitor diffusion loss convergence to 4.0 target. S1 accuracy trending positive - expect 40% by step 35k. Need infrastructure stability - current session longest since step 20k. After step 50k: comprehensive v1/v3 benchmarks and confidence calibration analysis.