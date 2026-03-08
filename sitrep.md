## v3 Training Status
**Step 4500/50000 (9.0%)** | A10G @ 100% util, 210W/300W, 60°C | **0.23 steps/s** | ETA: **54.5 hours** | Spot: **$0.46/hr** (62% savings) | Current session cost: **$2.60**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 1000 | 21.29 | 6.75 | 5.04% | 0.557 | 0.006 |
| 2000 | 22.53 | 6.54 | 6.44% | 0.613 | 0.004 |
| 3000 | 23.17 | 6.38 | 7.57% | 0.638 | 0.010 |
| 4000 | **23.71** | **6.29** | **8.46%** | **0.672** | **0.011** |

**Concerning trend**: AR perplexity degrading (+11% since step 1000). Diffusion loss improving steadily. S1 accuracy climbing but very slowly. AUROC progressing well. ECE wobbling but acceptable.

## Target Scorecard
- ❌ **AR PPL < 40**: 23.71 (✓ met, trending worse)
- ❌ **AUROC > 0.75**: 0.672 (89% there, good trend)  
- ✅ **ECE < 0.05**: 0.011 (well under target)
- ❌ **Diff loss → 4.0**: 6.29 (steady -0.46 drop, 57% progress)
- ❌ **S1 accuracy → 40%**: 8.46% (very slow climb, concerning)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. **Current AR performance significantly better than v1** (23.71 vs 43.86), but **S1 severely underperforming** (8% acc vs target 40%).

## Infrastructure  
**Current session**: 5.7h uptime, no interruptions. **Previous session**: i-0b467969 terminated after 6.8h (steps 400-1000). **Total cost**: $5.68 across 2 sessions. Spot pricing stable at $0.46/hr. 16GB/23GB VRAM utilization healthy.

## What's Next
**Red flag**: S1 token accuracy growth rate suggests **40% target unreachable** at current pace. Need to investigate S1 head learning dynamics. AR regression also concerning - may need LR schedule adjustment. Next major checkpoint at step 5000.