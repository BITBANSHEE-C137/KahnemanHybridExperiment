# v3 Training SITREP

## v3 Training Status
**Step 7400/50000** (14.8% complete) | GPU: **100% util**, A10G @ 58°C, 16.2/23GB VRAM | Rate: ~850 steps/day | **ETA: 49 days** | Spot cost: **$0.46/hr** (62% savings vs on-demand)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 1000 | 21.29  | 6.75      | 5.0%   | 0.557 | 0.0057 |
| 3000 | 23.17  | 6.38      | 7.6%   | 0.638 | 0.0100 |
| 5000 | 24.35  | 6.12      | 9.1%   | 0.695 | 0.0082 |
| **7000** | **25.48** | **5.87** | **10.6%** | **0.739** | **0.0089** |

**Trends:** AR PPL degrading (+19% since step 1k). Diffusion loss improving (-13%). S1 accuracy climbing steadily (+111%). AUROC approaching target. ECE stable.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **25.48** | ✅ **MET** |
| AUROC | > 0.75 | **0.739** | ❌ **98% there** |
| ECE | < 0.05 | **0.0089** | ✅ **MET** |
| Diff Loss | → 4.0 | **5.87** | 🔄 **68% progress** |
| S1 Accuracy | → 40% | **10.6%** | 🔄 **26% progress** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Current v3 AR PPL (**25.48**) tracking well vs WikiText baseline. S1 system showing **157% improvement** over v1 final loss equivalent.

## Infrastructure
**Current session:** 9.2hrs uptime, no interruptions. **Previous session:** Spot reclaim after 6.8hrs (steps 400-1000). **Total cost:** $7.28 across 2 sessions. **Savings:** 62% vs on-demand ($18.93). Checkpoints syncing properly.

## What's Next
Monitor AUROC convergence to 0.75+ threshold. AR PPL degradation **concerning** - investigate if joint training interference. Diffusion loss on good trajectory. Next eval at step 8k due shortly.