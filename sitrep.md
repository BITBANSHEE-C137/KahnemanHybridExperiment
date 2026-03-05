# ML Ops SITREP - v2 Training

## v2 Training Status
**Step 15,100/50,000 (30.2%)** | A10G @ **99% util** | **201W/300W** (52°C)  
Rate: ~3.1 steps/min | **ETA: 19.3 days** | Spot: **$0.44/hr** (64% savings)  
Current session uptime: **1.8hrs** | Total cost: **$10.74**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 8000 | 27.58 | 4.65 | 21.1% | 0.845 | 0.007 |
| 10000 | 28.39 | 4.37 | 25.1% | 0.850 | 0.004 |
| 12000 | 29.35 | 4.34 | 25.6% | 0.852 | 0.009 |
| 14000 | 30.34 | 4.31 | 26.0% | 0.853 | 0.011 |
| **15000** | **31.05** | **4.33** | **26.1%** | **0.853** | **0.014** |

**⚠️ AR PPL degrading** (+3.5 since step 8k). Diffusion loss stable ~4.3. **S1 accuracy climbing** steadily (+5%). AUROC plateaued. **ECE trending up** - calibration regressing.

## Target Scorecard
- **AR PPL < 40**: ✅ **31.05** (on track)
- **AUROC > 0.75**: ✅ **0.853** (strong)  
- **ECE < 0.05**: ✅ **0.014** (good but rising)
- **Diff loss → 4.0**: 🟡 **4.33** (close, needs improvement)
- **S1 accuracy → 40%**: 🔴 **26.1%** (behind, improving slowly)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**v2 AR already outperforming v1** (31.05 vs 43.86 PPL). S1 loss comparable to v1 final.

## Infrastructure
**10 spot sessions**, 5 reclaims in 2 days - aggressive spot market. Mixed g5.xlarge/2xlarge.  
Current: us-east-1f, stable 1.8hrs. **Total: $10.74 vs $53.36 on-demand**  
Checkpoints syncing normally (1.5GB), trainer healthy.

## What's Next
Monitor AR PPL trend - **concerning degradation**. S1 accuracy too slow for 40% target. Consider diffusion loss schedule adjustment. Post-training: comprehensive v1/v2 benchmarks, confidence calibration deep-dive.