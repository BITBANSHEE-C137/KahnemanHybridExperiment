# v2 Training SITREP - Step 16,400/50k

## v2 Training Status
**Progress**: 32.8% complete (16,400/50k steps)  
**GPU**: A10G @ 100% util, 201W/300W, 52°C, 16.6/23GB VRAM  
**Rate**: ~1.57 steps/sec, **ETA**: ~5.9 days  
**Spot Cost**: $0.44/hr (63.9% savings), $11.40 total, **$19.22 projected**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 10k  | 28.39  | 4.37      | 25.1%  | 0.850 | 0.004 |
| 12k  | 29.35  | 4.34      | 25.6%  | 0.852 | 0.009 |
| 14k  | 30.34  | 4.31      | 26.0%  | 0.853 | 0.011 |
| 16k  | **30.79** | **4.13** | **26.8%** | **0.860** | **0.007** |

**Trends**: AR PPL slowly degrading (+8% since 10k). Diffusion loss improving. S1 accuracy steady climb. AUROC trending up. ECE volatile but acceptable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.79** | ✅ |
| AUROC > 0.75 | **0.860** | ✅ |
| ECE < 0.05 | **0.007** | ✅ |
| Diff loss → 4.0 | **4.13** | 🟡 (96.7%) |
| S1 accuracy → 40% | **26.8%** | ❌ (67%) |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**v2 status**: AR on track vs v1 (30.79 < 43.86), diffusion converging to v1 target

## Infrastructure
**Current**: g5.2xlarge us-east-1f, 3.3h uptime  
**Spot History**: 10 sessions, 8 reclaims in 48h (**high churn**)  
**Issue**: Multiple g5.xlarge failures (sessions 4,5,9) - recommend sticking to 2xlarge  
**Cost Efficiency**: 64% savings maintained despite interruptions

## What's Next
Post-v2: Full benchmark suite, v1/v2 head-to-head on LAMBADA/WikiText, confidence calibration analysis. **Priority**: S1 accuracy gap needs investigation - only 67% to target.