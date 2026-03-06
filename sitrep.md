# SITREP: v2 Training Progress

## v2 Training Status
**Step 39,800/50,000 (79.6%)** - GPU: 100% util, 196W/300W, 53°C, 16.6GB/23GB VRAM  
Rate: ~380 steps/hr | ETA: **27 hours** | Current spot: $0.46/hr (62.7% savings)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 32000 | 31.39  | 3.96      | 28.4%  | 0.871 | 0.013 |
| 34000 | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 36000 | 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 38000 | 30.44  | 4.28      | 26.7%  | 0.865 | 0.004 |
| 39000 | **30.41** | **3.80** | **30.7%** | **0.863** | **0.007** |

**Trends:** AR PPL steadily improving ✓ | Diff loss volatile but trending down ✓ | S1 accuracy strong recovery from mid-30k dip ✓ | AUROC stable ~0.86 ✓ | ECE excellent calibration ✓

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **30.41** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.007** | ✅ **MET** |
| Diff loss → 4.0 | **3.80** | ✅ **MET** |
| S1 accuracy → 40% | **30.7%** | ⚠️ **77% THERE** |

**4/5 targets met** - S1 accuracy trending up strongly, likely to hit 40% by completion.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  

**Current v2 vs v1:** AR PPL **improved** (30.41 vs 43.86), diff loss **comparable** to S1 loss, confidence calibration **excellent**.

## Infrastructure
**13 spot sessions**, total cost **$25.55** vs $32.48 on-demand  
Current session: 14.4hr uptime, no interruptions since 01:33 UTC  
Checkpoint sync active, last saved: step_39000.pt (1.5GB)

## What's Next
**10,200 steps remaining** (~27hr) → v2 benchmarks → comprehensive v1 vs v2 comparison → confidence head effectiveness analysis → production readiness assessment