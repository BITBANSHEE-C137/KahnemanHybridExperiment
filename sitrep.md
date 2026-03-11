# v3 Training SITREP

## v3 Training Status
**Step 49,000/50,000** (98.0% complete). GPU maxed at **100% util**, 72W/72W, 82°C. Current L4 spot rate **$0.46/hr** (52.6% savings vs on-demand). **ETA: ~1 hour** to completion.

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 42000 | 28.33  | 3.89      | 29.1%   | 0.870 | 0.013 |
| 43000 | 28.14  | 4.20      | 25.9%   | 0.869 | 0.010 |
| 44000 | 28.07  | 4.40      | 24.9%   | 0.867 | 0.010 |
| 45000 | 27.95  | 4.16      | 26.5%   | 0.870 | 0.011 |
| 46000 | 28.13  | 3.94      | 28.1%   | 0.866 | 0.016 |
| 47000 | 28.09  | 3.88      | 29.3%   | 0.870 | 0.014 |
| 48000 | 28.04  | 4.19      | 26.1%   | 0.870 | 0.012 |
| 49000 | 28.05  | 4.41      | 24.9%   | 0.867 | 0.012 |

**AR PPL stalled** around 28 (good). **Diffusion loss unstable** (3.8-4.4 range, trending up). **S1 accuracy declining** (29.3% → 24.9%). **AUROC stable** ~0.867-0.870. **ECE excellent** <0.02.

## Target Scorecard
| Metric      | Target | Current | Status |
|-------------|--------|---------|---------|
| AR PPL      | <40    | **28.05** | ✅ |
| AUROC       | >0.75  | **0.867** | ✅ |
| ECE         | <0.05  | **0.012** | ✅ |
| Diff Loss   | →4.0   | **4.41**  | ❌ (trending away) |
| S1 Accuracy | →40%   | **24.9%** | ❌ (declining) |

**3/5 targets met**. Diffusion & S1 components underperforming.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **v3 AR matching v1 performance** (28 vs 43.86 PPL improvement). **S1 loss comparable** to v1 baseline.

## Infrastructure
**22 spot sessions**, $39.46 total cost. Current g6.2xlarge stable 7h runtime. **Heavy reclaim period** on 3/9 (11 short-lived instances). Switched to us-east-1a for better availability. **No recent interruptions**.

## What's Next
**1000 steps to completion**. Monitor diffusion loss drift and S1 accuracy decline. Post-completion: full benchmark suite, confidence calibration analysis, compare joint training vs separate AR/diffusion losses.