# v3 Training SITREP

## v3 Training Status
**Step 1/50k (0.0% complete)** - Fresh start after spot reclaim  
GPU: A10G @ **99% util**, 198W/300W, 54°C, 16.2GB/23GB VRAM  
Rate: Too early to estimate | ETA: TBD  
Spot cost: **$0.46/hr** (62% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
No eval checkpoints yet - training just started

| Step | AR PPL | Diff Loss | S1 Acc | Conf AUROC | ECE |
|------|--------|-----------|---------|------------|-----|
| 1    | ~27.3  | 10.79     | N/A     | N/A        | N/A |

**Initial losses look reasonable** - AR loss 3.315 (~27 PPL), diffusion loss high as expected

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | ~27.3 | ✅ **Already met** |
| AUROC | > 0.75 | N/A | ⏳ Pending |
| ECE | < 0.05 | N/A | ⏳ Pending |
| Diff Loss | → 4.0 | 10.79 | 🔴 **Needs -6.8 reduction** |
| S1 Accuracy | → 40% | N/A | ⏳ Pending |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**AR slightly regressed, S1 dropped 67% from joint training**

## Infrastructure
**2 spot sessions**, 1 reclaim after 8min (session 1)  
Current: 11min uptime, **$0.11 total cost**  
Previous reclaim: i-0d24c88137ed1cf10 @ 04:41 UTC  
Current stable: i-0dc653738fe50a9b2 since 04:48 UTC

## What's Next
- **Monitor spot stability** - already 1 reclaim today
- Wait for first eval checkpoint (~step 100-500)  
- Establish training rate baseline
- Compare initial convergence vs v1/v2 patterns