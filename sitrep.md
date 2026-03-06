# v2 Training SITREP

## v2 Training Status
**Step 28,500/50,000 (57%)** | GPU: 100% util, 198W/300W | Rate: ~1.45 steps/sec | **ETA: ~4h 10m** | Spot: $0.45/hr (63% savings vs $1.21 on-demand)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 21000 | 30.88  | 4.85      | 20.7%   | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%   | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%   | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%   | 0.863 | 0.005 |
| 25000 | 31.22  | 4.20      | 27.6%   | 0.860 | 0.012 |
| 26000 | 31.46  | 4.06      | 28.0%   | 0.863 | 0.018 |
| 27000 | 31.46  | 4.48      | 24.4%   | 0.862 | 0.009 |
| **28000** | **31.32** | **3.95** | **28.2%** | **0.872** | **0.007** |

**Trends**: AR PPL stable ~31. **Diffusion loss improving** (3.95, lowest yet). S1 accuracy volatile 24-28%. **AUROC trending up** to 0.872. ECE well-controlled.

## Target Scorecard
- AR PPL < 40: **✓ 31.32** 
- AUROC > 0.75: **✓ 0.872**
- ECE < 0.05: **✓ 0.007**
- Diff loss → 4.0: **✓ 3.95** (achieved!)
- S1 accuracy → 40%: **✗ 28.2%** (need +12pp)

**4/5 targets met**. S1 accuracy lagging significantly.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL

Current v2 AR PPL (**31.32**) significantly better than v1 WikiText (**43.86**). v2 diffusion loss (**3.95**) approaches v1 S1 loss (**4.12**).

## Infrastructure
Current session: 5.6h uptime, **12 total sessions**, $2.54 spent this run
**Total project cost: $18.98** | Multiple spot reclaims but good recovery
Recent stability: no interruptions last 5.6h in us-east-1a

## What's Next
**21,500 steps remaining** (~4h). Focus: **S1 accuracy breakthrough needed**. Post-completion: comprehensive v2 benchmarks, head-to-head v1 vs v2 analysis, confidence calibration deep-dive.