# ML Ops SITREP - v3 Training Status

## v3 Training Status
**CRITICAL**: Training appears stalled at **step 0/50k (0.0%)**. GPU idle (0% util), trainer process running but not progressing. Last checkpoint from 16:07 UTC suggests training halted ~4hrs ago. Current g6.xlarge spot rate: **$0.38/hr (52% savings)**. Issue requires immediate investigation.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 13000 | 28.41  | 4.42      | 24.1%  | 0.844 | 0.011  |
| 14000 | 28.51  | 4.29      | 24.7%  | 0.852 | 0.009  |
| 15000 | 28.64  | 4.50      | 23.7%  | **0.864** | **0.005** |
| 16000 | 28.66  | 4.38      | 23.5%  | 0.856 | 0.010  |
| 17000 | 28.89  | 4.34      | 25.2%  | 0.858 | 0.008  |
| 18000 | 28.99  | 4.44      | 23.0%  | 0.858 | 0.010  |
| 19000 | 29.21  | 4.39      | 22.1%  | **0.866** | 0.011  |
| 20000 | **29.22** | **4.24** | **26.8%** | 0.857 | **0.005** |

**Trends**: AR perplexity creeping up (+0.8 from 13k), but confidence calibration improving (ECE dropping). S1 accuracy volatile but recent uptick. AUROC peaked at 19k.

## Target Scorecard

| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.22** | ✅ **MET** |
| AUROC > 0.75 | **0.857** | ✅ **MET** |
| ECE < 0.05 | **0.005** | ✅ **MET** |
| Diff loss → 4.0 | **4.24** | 🔄 **CLOSE** |
| S1 accuracy → 40% | **26.8%** | ❌ **NEED +13%** |

**3/5 targets met**. Diffusion loss trending toward target. S1 accuracy remains primary bottleneck.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. Current v3 AR performance (**29.22 PPL**) significantly better than v1 WikiText baseline. S1 loss improvement from 4.12→4.24 marginal.

## Infrastructure
**14 spot sessions, $16.27 total cost**. Heavy churn: 8 reclaims in 6hrs (17:12-19:52). Instance type switching (g5→g6) suggests availability issues. Current g6.xlarge stable 7min, but training stalled. Previous productive session: g5.2xlarge ran 23hrs (steps 1k→19.3k).

## What's Next
**IMMEDIATE**: Debug training halt. Check data pipeline, memory, or checkpoint corruption. Resume from step 20k checkpoint. Consider larger instance for stability. Post-resolution: continue to 50k steps, then comprehensive v1/v2/v3 benchmark comparison.