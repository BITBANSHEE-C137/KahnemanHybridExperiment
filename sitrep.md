# v3 Training SITREP

## v3 Training Status
**Step 25,100/50,000 (50.2%)** | GPU: 100% util, 81°C | **~49.8k steps remaining**
Rate: ~12 steps/min | ETA: **~69 hours** | Spot: $0.46/hr (**53% savings**)
Current session: 2.1h uptime, $0.95 spent

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 18000 | 28.99  | 4.44      | 22.9%   | 0.858 | 0.0098 |
| 20000 | 29.22  | 4.24      | 26.8%   | 0.857 | 0.0048 |
| 22000 | 29.70  | **3.95**  | **28.3%** | **0.876** | 0.0039 |
| 25000 | **29.48** | 4.08   | 26.5%   | 0.861 | **0.0042** |

**Trends**: AR PPL stable ~29-30. Diff loss volatile but trending toward target. S1 accuracy peaked at 22k, now plateaued. **AUROC hit 0.876 then regressed**. ECE excellent throughout.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.48** | ✅ **MET** |
| AUROC > 0.75 | **0.861** | ✅ **MET** |
| ECE < 0.05 | **0.0042** | ✅ **MET** |
| Diff loss → 4.0 | **4.08** | 🎯 **CLOSE** |
| S1 accuracy → 40% | **26.5%** | ❌ **66% there** |

**3/5 targets met**. Diff loss nearly there. **S1 accuracy stalled** - needs investigation.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL
**Current v3 AR PPL (29.48) significantly better than v1 (43.86)**

## Infrastructure
**19 spot sessions**, $20.94 total cost vs $43.43 on-demand
Recent instability: **Multiple reclaims 3/9 17:00-22:00 UTC** (steps 20k-21k)
Current g6.2xlarge stable 2h+, good rates in us-east-1a

## What's Next
**S1 accuracy plateau concerning** - may need lr/architecture adjustments
Continue to 50k steps (~3 days). Post-completion: benchmarks vs v1, confidence head analysis for AUROC regression investigation.