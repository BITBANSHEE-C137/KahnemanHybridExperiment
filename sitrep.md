# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 34,500/50,000 (69%)** | Rate: ~520 steps/hr | **ETA: 30 hours**  
**GPU**: L4 @ 99% util, 72W, 73°C, 16.6GB/23GB VRAM  
**Spot**: $0.46/hr (53% savings) | Current session: 18.1hrs uptime

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 27000 | 29.55  | 4.316     | 24.6%  | 0.866 | 0.0109 |
| 30000 | 29.16  | 4.337     | 24.6%  | 0.868 | 0.0046 |
| 32000 | 29.04  | 4.350     | 24.2%  | 0.865 | 0.0089 |
| **34000** | **28.85** | **4.149** | **25.6%** | **0.871** | **0.0069** |

**Trends**: AR PPL improving steadily (-2.4%). Diff loss volatile but trending down. S1 accuracy stuck ~25%. AUROC solid, ECE excellent.

## Target Scorecard
- **AR PPL < 40**: ✅ **28.85** (target met)
- **AUROC > 0.75**: ✅ **0.871** (strong)  
- **ECE < 0.05**: ✅ **0.0069** (excellent calibration)
- **Diff Loss → 4.0**: 🟡 **4.15** (close, trending down)
- **S1 Accuracy → 40%**: ❌ **25.6%** (stuck, concerning)

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Gap**: AR slightly regressed in joint training, but S1 loss dropped 67%

## Infrastructure
**19 spot sessions** | **Total cost: $28.29** vs $43.42 on-demand  
Current: g6.2xlarge, 18hrs stable, no recent reclaims  
**Risk**: Multiple short sessions 3/9 suggest spot volatility in us-east-1b

## What's Next
**S1 accuracy plateau is concerning** - investigate token prediction head or data distribution. Continue to step 50k, then comprehensive v2 benchmarks vs v1 baselines. Confidence calibration looks promising for deployment.