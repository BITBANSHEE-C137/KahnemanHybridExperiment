# v3 Training Status SITREP

## v3 Training Status
**Step 14000/50000 (28%)** | GPU util **98%** A10G | Rate ~229 steps/hr | **ETA: 6.5 days** | Spot cost **$0.45/hr** (62% savings) | Total run cost **$10.97**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 10000| 27.55  | 4.98      | 19.0%  | 0.828 | 0.0053 |
| 11000| 27.85  | 4.43      | 22.0%  | 0.853 | 0.0102 |
| 12000| 28.12  | 4.31      | 25.0%  | 0.853 | 0.0066 |
| 13000| 28.41  | 4.42      | 24.1%  | 0.844 | 0.0110 |
| 14000| **28.51** | **4.29** | **24.7%** | **0.852** | **0.0087** |

**Trends**: AR perplexity plateauing around 28 (slight degradation). Diffusion loss converging to target. S1 accuracy stalled at ~24-25%. AUROC stable at 0.85+. ECE volatile but under target.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.51** | ✅ **MET** |
| AUROC > 0.75 | **0.852** | ✅ **MET** |
| ECE < 0.05 | **0.0087** | ✅ **MET** |
| Diff loss → 4.0 | **4.29** | 🔶 **CLOSE** |
| S1 accuracy → 40% | **24.7%** | ❌ **BEHIND** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v3 AR performance tracking well vs v1 baseline**.

## Infrastructure
**g5.2xlarge spot** | 17.1hr uptime | 2 sessions | **1 spot reclaim** on 3/8 (recovered cleanly) | 70% VRAM utilization | Temp 50°C nominal | Auto-sync active | Last checkpoint: step_14000.pt (1.5GB)

## What's Next
**S1 accuracy plateau concerning** - may need LR adjustment or architecture review. Diffusion loss on track to hit 4.0. Monitor for AR perplexity regression. Complete v3 by 3/16, then benchmark suite vs v1/v2 comparison.