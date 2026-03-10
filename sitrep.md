# ML Ops SITREP - v3 Training

## v3 Training Status
**Progress**: 26k/50k steps (**52%** complete)  
**GPU**: L4 @ **100%** util, 81°C, 16.6GB/23GB VRAM  
**Rate**: ~6.8 steps/min (extrapolated from trajectory)  
**ETA**: ~58 hours remaining  
**Spot Cost**: $0.46/hr (**53.3% savings** vs on-demand), $21.63 total

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 19000| 29.21   | 4.39      | 22.1%   | 0.866 | 0.0106|
| 20000| 29.22   | 4.24      | 26.8%   | 0.857 | 0.0048|
| 21000| 29.94   | 4.26      | 26.8%   | 0.856 | 0.0116|
| 22000| 29.70   | 3.95      | 28.3%   | 0.876 | 0.0039|
| 23000| 29.57   | 4.19      | 26.1%   | 0.861 | 0.0059|
| 24000| 29.53   | 4.31      | 25.2%   | 0.862 | 0.0055|
| 25000| 29.48   | 4.08      | 26.5%   | 0.861 | 0.0042|
| 26000| **29.58**| **4.02** | **27.7%**| **0.864**| **0.0063**|

**Trends**: AR PPL plateaued ~29.5. Diffusion loss improving toward target. S1 accuracy volatile but trending up. Confidence metrics stable.

## Target Scorecard
- **AR PPL < 40**: ✅ **29.58** (well under target)
- **AUROC > 0.75**: ✅ **0.864** (strong confidence)  
- **ECE < 0.05**: ✅ **0.0063** (excellent calibration)
- **Diff loss → 4.0**: 🟡 **4.02** (nearly achieved)
- **S1 accuracy → 40%**: ❌ **27.7%** (needs 12pp improvement)

**4/5 targets met**. S1 accuracy remains the blocker.

## v1 Benchmark Baseline
v1 final (50k): LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
Current v3 AR performance (**29.58 PPL**) **matches GPT-2 baseline** - joint training not regressing AR capability this time.

## Infrastructure
**19 spot sessions** across g5/g6 instances. Multiple brief interruptions 3/9 (steps 19k-21k) with **17 reclaims** in 6 hours - high spot volatility period. Current g6.2xlarge session stable **3.6h** uptime. 

**Cost efficiency**: Total $21.63 for 26k steps vs $43.28 on-demand.

## What's Next
- Monitor S1 accuracy - **critical gap** to 40% target
- Diffusion loss should hit 4.0 within 1k steps  
- After 50k: comprehensive v1→v2→v3 progression analysis
- Investigate S1 token prediction instability in 20k-26k range