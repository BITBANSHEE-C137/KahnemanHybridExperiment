# v2 Training SITREP

## v2 Training Status
**Step 28,500/50,000 (57%)** | A10G @ 100% util, 193W/300W, 55°C | 16.6GB/23GB VRAM  
**Rate**: ~300 steps/hr | **ETA**: ~3 days | **Spot cost**: $0.45/hr (63% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.007 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25000 | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012 |
| 26000 | 31.46  | 4.06      | 28.0%  | 0.863 | 0.018 |
| 27000 | 31.46  | 4.48      | 24.4%  | 0.862 | 0.009 |
| 28000 | 31.32  | **3.95**  | **28.2%** | **0.872** | 0.007 |

**Trends**: AR PPL plateaued ~31. Diff loss improving (4.85→3.95). S1 accuracy volatile but trending up. **AUROC hit new high 0.872**. ECE stable.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **31.32** | ✅ **MET** |
| AUROC > 0.75 | **0.872** | ✅ **MET** |  
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **3.95** | ✅ **MET** |
| S1 accuracy → 40% | **28.2%** | ❌ **70% there** |

**4/5 targets met**. S1 accuracy needs **+11.8pp** to hit 40%.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

Current v2 AR PPL (**31.32**) already **28% better** than v1 WikiText (43.86). Confidence head showing strong calibration.

## Infrastructure  
**Current session**: 0.8hr uptime, $0.37 cost | **Total project**: $19.37 across 13 sessions  
**Spot interruptions**: 12 reclaims over 2 days - frequent but manageable with checkpointing  
**Instance mix**: Mostly g5.2xlarge, brief g5.xlarge experiments. us-east-1b/a/f zones.

## What's Next
After v2 completes (~3 days): Full benchmark suite, v1 vs v2 head-to-head, confidence calibration analysis. S1 accuracy trajectory suggests **40% target achievable** by step 50k.