# v3 Training SITREP

## v3 Training Status
**COMPLETED** at step **50,000/50,000** (100%). GPU idle (0% util, 16W power). Training finished ~1.5h ago. Final rate ~1.6 steps/sec over 8.5h runtime. Current instance: g6.2xlarge spot @ $0.46/hr (52.6% savings vs on-demand).

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 43k   | 28.14  | 4.196     | 25.9%  | 0.869 | 0.0103 |
| 44k   | 28.07  | 4.404     | 24.9%  | 0.867 | 0.0096 |
| 45k   | 27.95  | 4.159     | 26.5%  | 0.870 | 0.0112 |
| 46k   | 28.13  | 3.943     | 28.1%  | 0.866 | 0.0155 |
| 47k   | 28.09  | 3.883     | 29.3%  | 0.870 | 0.0144 |
| 48k   | 28.04  | 4.192     | 26.1%  | 0.870 | 0.0120 |
| 49k   | 28.05  | 4.407     | 24.9%  | 0.867 | 0.0121 |
| **50k** | **27.99** | **4.163** | **26.5%** | **0.871** | **0.0125** |

**Trends**: AR PPL stable ~28, slight improvement at end. Diff loss volatile (3.88→4.41). S1 accuracy peaked at 29.3% (47k) but regressed. AUROC steady ~0.87. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **27.99** | ✅ **MET** |
| AUROC > 0.75 | **0.871** | ✅ **MET** |
| ECE < 0.05 | **0.0125** | ✅ **MET** |
| Diff loss → 4.0 | **4.163** | ❌ Close (4.1% over) |
| S1 accuracy → 40% | **26.5%** | ❌ **34% gap** |

**3/5 targets met**. S1 accuracy significantly underperforming.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. v3 shows **AR improvement** (27.99 vs 43.86 WikiText est.) but **S1 stagnation** (26.5% acc vs target 40%). Joint training trade-offs evident.

## Infrastructure  
**22 spot sessions**, **40.3% uptime** across 4 days. **7 reclaims** on 3/9 (spot instability). Current session: 9.9h stable on g6.2xlarge. Total cost: **$40.27** (52.6% savings). Robust checkpoint strategy handled interruptions well.

## What's Next
Training complete. **Immediate**: Run full v3 benchmarks (LAMBADA, WikiText-103). **Analysis**: v1→v3 comparison, investigate S1 underperformance, confidence calibration deep-dive. Consider S1 loss weighting adjustments for v4.