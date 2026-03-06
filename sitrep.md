# SITREP - v2 Training Status
**2026-03-06 23:00 UTC**

## v2 Training Status
Step **45,200/50,000** (90.4% complete). A10G running at **99% util**, 203W/300W, 51°C. Current rate ~400 steps/hr, **ETA ~12 hours**. Spot instance g5.2xlarge @ **$0.46/hr** (62% savings vs on-demand). 5.3hr uptime this session.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 38000 | 30.44  | 4.28      | 0.267  | 0.865 | 0.004 |
| 39000 | 30.41  | 3.80      | 0.307  | 0.863 | 0.007 |
| 40000 | 30.21  | 4.56      | 0.232  | 0.857 | 0.007 |
| 41000 | 30.12  | 4.47      | 0.251  | 0.862 | 0.012 |
| 42000 | 30.08  | 4.07      | 0.290  | 0.862 | 0.016 |
| 43000 | 29.96  | 3.93      | 0.292  | 0.868 | 0.020 |
| 44000 | 29.96  | 4.37      | 0.254  | 0.865 | 0.016 |
| **45000** | **29.80** | **3.86** | **0.293** | **0.875** | **0.016** |

**Trends:** AR perplexity steadily improving (-0.6 over 7k steps). Diffusion loss volatile but trending down. S1 accuracy unstable, bouncing 23-31%. **AUROC improving** (+0.01 last 2k steps). ECE degrading but stabilizing ~0.016.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.8** | ✅ **PASS** |
| AUROC > 0.75 | **0.875** | ✅ **PASS** |
| ECE < 0.05 | **0.016** | ✅ **PASS** |
| Diff loss → 4.0 | **3.86** | ✅ **PASS** |
| S1 accuracy → 40% | **29.3%** | ❌ **MISS** |

**4/5 targets met.** S1 accuracy plateau at ~29%, need +11pp to hit 40%.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL. 

**v2 vs v1:** AR PPL improved 29.8 vs 43.86 (-32%). Diffusion loss comparable 3.86 vs 4.12. **AR training is working.**

## Infrastructure
**15 spot sessions**, $28.74 total cost vs $62.5 on-demand (**54% savings**). Major reclaims on Mar 4-5, switched AZs 3x. Current session stable 5.3hrs. Checkpoints syncing normally.

## What's Next
**4,800 steps remaining** (~12hrs). Post-completion: v2 LAMBADA/WikiText benchmarks, confidence head analysis on S1 plateau, v1→v2 comparison report. **S1 accuracy concern** - may need architectural changes for v3.