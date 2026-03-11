# v3 Training SITREP - 2026-03-11 06:30 UTC

## v3 Training Status
**Step 39,500/50,000 (79.0%)** | A10G @ 98% util, 201W/300W | **2.03h ETA** | Spot: **$0.44/hr** (63% savings) | Current session cost: **$0.90**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 32000 | 29.04  | 4.35      | 24.2%   | 0.865 | 0.009 |
| 33000 | 28.93  | 4.09      | 26.6%   | 0.861 | 0.009 |
| 34000 | 28.85  | 4.15      | 25.6%   | 0.871 | 0.007 |
| 35000 | 28.73  | 4.26      | 25.0%   | 0.863 | 0.006 |
| 36000 | 28.59  | 4.46      | 23.5%   | 0.864 | 0.011 |
| 37000 | 28.51  | 4.52      | 24.1%   | 0.856 | 0.006 |
| 38000 | 28.43  | 4.02      | 28.5%   | 0.864 | 0.009 |
| 39000 | **28.34** | **4.04** | **29.0%** | **0.863** | **0.011** |

**Trends**: AR PPL improving steadily (-0.70 over 7k steps). Diff loss volatile but trending toward target. S1 accuracy surged +4.5% recently. AUROC stable ~0.86. ECE well-controlled.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.34** | ✅ **MET** |
| AUROC | > 0.75 | **0.863** | ✅ **MET** |
| ECE | < 0.05 | **0.011** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.04** | ✅ **AT TARGET** |
| S1 Accuracy | → 40% | **29.0%** | ⚠️ **+11% needed** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **v3 AR already outperforms v1 WikiText baseline** (28.34 vs 43.86). S1 accuracy gap remains significant.

## Infrastructure
**20 sessions, $31.92 total cost**. Current g5.2xlarge stable 2h+ (us-east-1f). Previous session chaos 3/9: **12 spot reclaims** in 4h (steps 19k-24k) due to us-east-1b volatility. Switched to us-east-1a/f for stability. Long g6.2xlarge session (24h, $11.02) carried training 25k-38k.

## What's Next
**10.5k steps remaining** (~21h at current rate). Post-completion: v3 benchmarks vs v1/GPT-2, confidence calibration deep-dive, S1 token analysis. Expecting final AR PPL ~27.5, S1 accuracy plateau ~32-35%.