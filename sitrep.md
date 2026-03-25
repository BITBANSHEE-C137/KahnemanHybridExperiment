# v4 Training SITREP

## v4 Training Status
**Progress**: 42,300/75,000 steps (**56.4%**) | **Rate**: ~13 steps/min | **ETA**: ~42h  
**GPU**: A10G at **100%** util, 205W/300W, 57°C, 16.6/23GB VRAM  
**Spot Cost**: $0.45/hr (**63.8% savings**), projected $32.52 total

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 38500 | 29.30  | 4.28      | 28.0%  | 0.858 | 0.012  |
| 39000 | 29.17  | 4.08      | 30.5%  | 0.857 | 0.008  |
| 40000 | 29.05  | 3.79      | 32.7%  | 0.862 | 0.018  |
| 41000 | 28.84  | 3.94      | 30.9%  | 0.864 | 0.016  |
| 42000 | **28.80** | **4.02** | **30.2%** | **0.861** | **0.006** |

**Trends**: AR PPL improving steadily (-1.7%). Diff loss volatile but trending toward target. S1 accuracy plateau ~30%. AUROC stable. **ECE excellent** at 0.006.

## Target Scorecard
- **AR PPL < 40**: ✅ **28.8** (28% below target)
- **AUROC > 0.75**: ✅ **0.861** (15% above target)  
- **ECE < 0.05**: ✅ **0.006** (88% below target)
- **Diff Loss → 4.0**: ✅ **4.02** (at target)
- **S1 Accuracy → 40%**: ❌ **30.2%** (25% below target)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v4 AR performance on track to match/exceed v1**

## Infrastructure
**Current**: g5.2xlarge in us-east-1e, 13.5h uptime, stable  
**History**: 73 spot sessions, frequent reclaims days 1-2, stabilized since step 35k  
**Total Cost**: $54.36 actual vs $88.38 on-demand (**38% savings**)

## What's Next
S1 accuracy **stalled at 30%** - investigate token prediction head or diffusion coupling. All other metrics **exceeding targets**. Training stable, expect completion in ~2 days at current rate.