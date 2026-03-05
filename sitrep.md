# v2 Training SITREP

## v2 Training Status
**Step 18,400/50,000** (36.8% complete) • A10G at **100% GPU util**, 200W/300W • **5.8 hrs uptime** • Rate: ~3.2 steps/min • **ETA: ~6.8 days** • Current spot: **$0.44/hr** (64% savings vs on-demand $1.21/hr) • **Total cost: $12.49**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 11000| 28.91  | 4.19     | 25.97%  | 0.857 | 0.005|
| 12000| 29.35  | 4.34     | 25.63%  | 0.852 | 0.009|
| 13000| 30.50  | 4.40     | 25.46%  | 0.852 | 0.012|
| 14000| 30.34  | 4.31     | 25.96%  | 0.853 | 0.011|
| 15000| 31.05  | 4.33     | 26.09%  | 0.852 | 0.014|
| 16000| 30.79  | 4.13     | 26.82%  | 0.860 | 0.007|
| 17000| 30.70  | 4.52     | 23.65%  | 0.860 | 0.007|
| **18000**| **30.77** | **4.03** | **27.23%** | **0.869** | **0.006**|

**Trends:** AR PPL **degrading** (~2pt increase). AUROC **improving** (+0.012). ECE **volatile** but acceptable. **S1 acc recovery** after step 17k dip.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.77** | ✅ **MET** |
| AUROC > 0.75 | **0.869** | ✅ **MET** |
| ECE < 0.05 | **0.006** | ✅ **MET** |
| Diff loss → 4.0 | **4.03** | ✅ **MET** |
| S1 accuracy → 40% | **27.23%** | ❌ **68% to target** |

**3/5 targets met.** S1 accuracy **lagging significantly** behind 40% target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12 • GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL • **AR slightly regressed** from joint training; **S1 loss dropped 67%** in v1

## Infrastructure
**10 spot sessions**, 8 reclaims across us-east-1a/b/f • **Stable 5.8hr** current session in us-east-1f • Mixed g5.xlarge/2xlarge instances • **Total: $12.49** vs $53.34 on-demand (77% savings)

## What's Next
**Concerns:** AR PPL trending up, S1 acc plateau. After v2 completes: v2 benchmarks, confidence head analysis, investigate **AR-S1 optimization conflict**. Consider **S1 loss weighting adjustment**.