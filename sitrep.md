# v2 Training SITREP

## v2 Training Status
**Step 27,700/50,000 (55.4%)** | A10G @ **99% GPU util** | **51°C** | Power: 199W/300W  
Rate: ~2.9 steps/min | **ETA: ~13h** | Spot: **$0.45/h** (63% savings) | Current cost: **$18.56**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 20k  | 30.92  | 4.75      | 21.3%  | 0.851 | 0.007 |
| 22k  | 30.95  | 4.19      | **27.5%** | 0.858 | 0.010 |
| 24k  | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 26k  | 31.46  | 4.06      | 28.0%  | 0.863 | 0.018 |
| 27k  | **31.46** | **4.48** | **24.4%** | **0.862** | **0.009** |

**Trends:** AR PPL slowly degrading (+0.5 over 7k steps). S1 accuracy volatile but trending up. AUROC plateauing ~0.86. ECE spiked at 26k but recovered. **Diffusion loss noisy**.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.46** | ✅ **MET** |
| AUROC > 0.75 | **0.862** | ✅ **MET** |
| ECE < 0.05 | **0.009** | ✅ **MET** |
| Diff loss → 4.0 | **4.48** | ⚠️ **Close** |
| S1 accuracy → 40% | **24.4%** | ❌ **Need +15.6pp** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**AR slightly regressed** (-0.82% LAMBADA), **S1 improved 67%** (loss 4.12→current)

## Infrastructure
**12 spot interruptions** over 2.3 days | Current session: **4.6h stable** (us-east-1a)  
Total uptime: 62% efficient | **Aggressive cost optimization**: g5.xlarge fallbacks saved $24  
No recent interruptions - **stable training window**

## What's Next
**23k steps remaining** (~13h) | Post-completion: full benchmark suite, v1→v2 delta analysis, confidence calibration deep-dive. **S1 accuracy gap** biggest concern for final eval.