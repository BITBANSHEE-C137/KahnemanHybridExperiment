# v2 Training SITREP

## v2 Training Status
**Step 28,100 / 50,000 (56.2% complete)**  
GPU: A10G @ **100% util**, 197W/300W, 47°C, 16.6GB/23GB VRAM  
Rate: ~275 steps/hr | **ETA: ~3.3 days**  
Spot cost: **$0.454/hr** (62.8% savings vs on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.0075 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.0096 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.0095 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.0050 |
| 25000 | 31.22  | 4.20      | 27.6%  | 0.860 | 0.0120 |
| 26000 | 31.46  | 4.06      | 28.0%  | 0.863 | 0.0177 |
| 27000 | 31.46  | 4.48      | 24.4%  | 0.862 | 0.0095 |
| 28000 | **31.32** | **3.95** | **28.2%** | **0.872** | **0.0073** |

**Trends:** Strong improvement at step 28k - diffusion loss **dropping** (3.95), AUROC **jumped** to 0.872, ECE excellent at 0.0073. AR PPL stable ~31. S1 accuracy volatile but trending up.

## Target Scorecard
- **AR PPL < 40**: ✅ **31.32** (target met)
- **AUROC > 0.75**: ✅ **0.872** (target met) 
- **ECE < 0.05**: ✅ **0.0073** (target met)
- **Diff Loss → 4.0**: ✅ **3.95** (target met!)
- **S1 Accuracy → 40%**: ❌ **28.2%** (need +11.8%)

**4/5 targets met** - only S1 accuracy lagging.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v2 AR performance (**31.32 PPL**) significantly better than v1 WikiText baseline (43.86).

## Infrastructure
**Current session**: 5.1h uptime, $2.28 spent  
**Total cost**: $18.75 across 12 sessions  
**Spot interruptions**: 11 reclaims (frequent but well-handled)  
Recent stability: Current instance running **5+ hours** without interruption

## What's Next
**22k steps remaining** (~3.3 days). Continue monitoring S1 accuracy - only missing target. Post-completion: comprehensive v2 benchmarks, direct v1 comparison, confidence calibration analysis.