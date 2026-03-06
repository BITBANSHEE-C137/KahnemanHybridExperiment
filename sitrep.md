# v2 Training SITREP

## v2 Training Status
**Step 31,500/50,000 (63.0%)** • A10G @ 100% util (192W/300W, 53°C) • 16.6/23.0GB VRAM  
Rate: ~2.1 steps/min • **ETA: ~146 hours** • Spot: $0.453/hr (62.8% savings) • Session cost: **$2.01**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | 0.005 |
| 25000 | 31.22 | 4.20 | 27.6% | 0.860 | 0.012 |
| 26000 | 31.46 | 4.06 | 28.0% | 0.863 | 0.018 |
| 27000 | 31.46 | 4.48 | 24.4% | 0.862 | 0.009 |
| 28000 | 31.32 | 3.95 | 28.2% | **0.872** | 0.007 |
| 29000 | 31.43 | 4.21 | 27.7% | 0.860 | 0.022 |
| 30000 | 31.68 | 4.08 | 28.1% | 0.864 | 0.023 |
| **31000** | **31.60** | **4.49** | **24.5%** | **0.862** | **0.014** |

**Trends**: AR PPL plateaued ~31.5. Diff loss volatile (3.95→4.49). S1 accuracy oscillating 24-28%. AUROC stable ~0.86. ECE variable but acceptable.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **31.6** | ✅ **MET** |
| AUROC | > 0.75 | **0.862** | ✅ **MET** |
| ECE | < 0.05 | **0.014** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.49** | ⚠️ **ABOVE** |
| S1 Acc | → 40% | **24.5%** | ❌ **BELOW** |

**3/5 targets met**. Diffusion loss regressed from 3.95 → 4.49. S1 accuracy stalled at ~25%.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Analysis**: AR slightly regressed vs GPT-2, S1 improved 67% from pretrained

## Infrastructure
**13 spot sessions** • Total cost: **$20.98** vs $32.52 on-demand (35% savings)  
Current session: 4.4hrs uptime, stable • **12 reclaims** across us-east-1 AZs  
Checkpoints: 29k/30k/31k synced, 1.5GB each

## What's Next
**18.5k steps remaining** (~6 days) • Post-completion: v2 benchmarks, v1→v2 delta analysis, confidence calibration deep-dive • **Priority**: Debug S1 accuracy plateau & diffusion loss volatility