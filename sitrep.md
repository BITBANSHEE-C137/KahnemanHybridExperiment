# v3 Training SITREP

## v3 Training Status
**Step 33k/50k (66%)** | L4 @ 100% util, 72W/72W, 80°C | **16.6GB/23GB VRAM** | Rate: ~500 steps/hr | **ETA: ~34h** | Current spot: **$0.46/hr** (53% savings) | **15.6h uptime**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 26k  | 29.58  | 4.02      | 27.7%  | 0.864 | 0.006 |
| 27k  | 29.55  | 4.32      | 24.6%  | 0.866 | 0.011 |
| 28k  | 29.40  | 4.51      | 23.8%  | 0.865 | 0.007 |
| 29k  | 29.36  | 4.27      | 25.5%  | 0.867 | 0.012 |
| 30k  | 29.16  | 4.34      | 24.6%  | 0.868 | 0.005 |
| 31k  | 28.95  | 4.47      | 23.3%  | 0.871 | 0.003 |
| 32k  | 29.04  | 4.35      | 24.2%  | 0.865 | 0.009 |
| **33k** | **28.93** | **4.09** | **26.6%** | **0.861** | **0.009** |

**Trends:** AR PPL steady decline ✓. Diff loss improving recent 2k steps ✓. S1 accuracy volatile but recovering ✓. AUROC plateau ~0.86. ECE erratic but low.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **28.93** | ✅ **PASS** |
| AUROC | > 0.75 | **0.861** | ✅ **PASS** |
| ECE | < 0.05 | **0.009** | ✅ **PASS** |
| Diff Loss | → 4.0 | **4.09** | 🟡 **Close** |
| S1 Acc | → 40% | **26.6%** | ❌ **Below** |

**3/5 targets met.** Diffusion loss nearly there. S1 accuracy needs 13.4pp improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR PPL (28.93) beating v1 (43.86) by 34%** ✅

## Infrastructure
**19 sessions, $27.17 total cost** | Current: g6.2xlarge us-east-1a | **Spot reclaim chaos 3/9-3/10** - 17 interruptions in 48h, mostly g5/g6 capacity issues | Stable since 3/10 04:25 UTC | Projected v3 total: **~$42**

## What's Next
**17k steps remaining** → Complete by 3/12 morning | Post-completion: v3 benchmarks, confidence head deep-dive, v1→v3 LAMBADA comparison, S1 accuracy analysis