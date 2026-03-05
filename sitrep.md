# v2 Training SITREP

## v2 Training Status
**Step 20,100/50,000 (40.2% complete)**  
A10G @ 100% util, 202W/300W, 52°C, 16.6/23GB VRAM  
Rate: ~7.8 steps/min, **ETA: 63 hours**  
Spot cost: **$0.44/hr** (64% savings vs on-demand $1.21/hr)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 13000 | 30.50 | 4.40 | 25.5% | 0.852 | 0.012 |
| 16000 | 30.79 | 4.13 | 26.8% | 0.860 | 0.007 |
| 18000 | 30.77 | 4.03 | 27.2% | 0.869 | 0.006 |
| 20000 | **30.92** | **4.75** | **21.3%** | **0.851** | **0.007** |

**⚠️ REGRESSION ALERT**: Diffusion loss spiked +18%, S1 accuracy crashed -22%, AUROC dropped. AR PPL stable but not improving.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.92** | ✅ MET |
| AUROC | > 0.75 | **0.851** | ✅ MET |  
| ECE | < 0.05 | **0.007** | ✅ MET |
| Diff Loss | → 4.0 | **4.75** | ❌ REGRESSED |
| S1 Accuracy | → 40% | **21.3%** | ❌ FAR BEHIND |

**3/5 targets met**. Diffusion and S1 performance concerning.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
v2 AR performance **worse than GPT-2 baseline**, S1 accuracy **half of target**.

## Infrastructure
**10 spot sessions, 9 reclaims in 32 hours**  
Total cost: **$13.33** (66% savings)  
Current session: 7.8hr uptime, us-east-1f stable  
Frequent interruptions impacting training stability

## What's Next
**Immediate**: Investigate diffusion/S1 regression around step 19-20k  
**Post-completion**: Full v2 benchmarks, confidence head ablation studies  
**Consider**: Learning rate schedule adjustment for joint training stability