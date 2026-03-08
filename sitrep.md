# SITREP: v3 Training Progress Report

## v3 Training Status
**Step 3,700/50,000 (7.4% complete)**  
GPU: A10G @ **100% util**, 210W/300W, 60°C, 16.2GB VRAM used  
Rate: ~0.23 steps/sec | **ETA: ~55 hours** | Spot cost: **$0.46/hr** (62% savings)

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|------|--------|-----------|--------|-------|--------|
| 1000 | 21.29  | 6.75      | 5.04%  | 0.557 | 0.0057 |
| 2000 | 22.53  | 6.54      | 6.44%  | 0.613 | 0.0036 |
| 3000 | **23.17** | **6.38** | **7.57%** | **0.638** | **0.0100** |

**Trends**: AR PPL slowly degrading (+8.8% from step 1k). Diffusion loss improving steadily (-5.5%). S1 accuracy climbing (+50% relative). **AUROC improving** but ECE regressed at latest checkpoint.

## Target Scorecard

| Target | Current | Met? |
|--------|---------|------|
| AR PPL < 40 | **23.17** | ✅ |
| AUROC > 0.75 | **0.638** | ❌ |
| ECE < 0.05 | **0.010** | ✅ |
| Diff loss → 4.0 | **6.38** | 🔄 |
| S1 accuracy → 40% | **7.57%** | 🔄 |

**2/5 targets met**. AUROC climbing but needs +18% to hit target. S1 accuracy trajectory positive but distant from 40%.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR performance ahead of v1 final** (23.17 vs 43.86 PPL)

## Infrastructure
**Active spot**: g5.2xlarge, 4.7h uptime, $2.14 spent  
**Session history**: 1 reclaim at step 1000 (cost: $3.11), smooth recovery  
**Total cost**: $5.22 across 2 sessions, **62% savings vs on-demand**

## What's Next
Monitor AUROC progression - **critical blocker** for targets. ECE regression needs investigation. Diffusion loss on good trajectory. **Expect 55hr completion** at current rate if no further spot reclaims.