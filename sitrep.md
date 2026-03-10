# v3 Training SITREP

## v3 Training Status
**Step 25,700/50,000 (51.4%)** | GPU: **100% util**, 73W@79°C | Rate: ~700 steps/3h | **ETA: 24h** | Spot: **$0.46/hr** (-53% savings)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 18000 | 28.99  | 4.44      | 0.230  | 0.858 | 0.0098 |
| 20000 | 29.22  | 4.24      | 0.268  | 0.857 | 0.0048 |
| 22000 | 29.70  | **3.95**  | **0.283** | **0.876** | 0.0039 |
| 24000 | 29.53  | 4.31      | 0.252  | 0.862 | 0.0055 |
| 25000 | **29.48** | 4.08   | 0.265  | 0.861 | **0.0042** |

**Trends:** AR PPL plateaued ~29.5. Diff loss volatile but trending toward target. **S1 accuracy regressed** from 22k peak. AUROC stable. ECE excellent.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | <40    | **29.48** | ✅ |
| AUROC  | >0.75  | **0.861** | ✅ |
| ECE    | <0.05  | **0.004** | ✅ |
| Diff Loss | →4.0 | **4.08** | 🟡 (close) |
| S1 Acc | →40%   | **26.5%** | ❌ (stalled) |

## v1 Benchmark Baseline  
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR performance superior to v1**, confidence head performing well.

## Infrastructure
**19 spot sessions**, frequent reclaims Mar 9 (14 interruptions). Current g6.2xl stable 3h+. **Total cost: $21.44** vs $43.33 on-demand. Session volatility cost ~$1.50 in restart overhead.

## What's Next
**S1 accuracy plateau concerning** - investigate tokenizer alignment. Monitor diff loss convergence to 4.0. Expect 25k more steps at current rate. Post-completion: comprehensive v1/v2 benchmarking, confidence calibration analysis.