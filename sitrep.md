# v2 Training SITREP

## v2 Training Status
**Step 41,000/50,000 (82%)** | GPU: 100% util, 194W/300W, 54°C | **Rate: ~720 steps/hr** | ETA: ~12.5hrs | Spot: **$0.46/hr** (63% savings vs on-demand)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 34000 | 31.13 | 4.68 | 22.0% | 0.854 | 0.009 |
| 36000 | 30.69 | 4.30 | 24.8% | 0.863 | 0.010 |
| 38000 | 30.44 | 4.28 | **26.7%** | 0.865 | 0.004 |
| 39000 | 30.41 | **3.80** | **30.7%** | 0.863 | 0.007 |
| 40000 | 30.21 | 4.56 | 23.2% | 0.857 | 0.007 |
| **41000** | **30.12** | 4.47 | 25.1% | **0.862** | **0.012** |

**Trends:** AR perplexity steadily improving. Diffusion loss volatile (3.80→4.56→4.47). S1 accuracy peaked at 30.7% (step 39k), now regressed to 25%. ECE degraded slightly.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|---------|---------|---------|
| AR PPL | < 40 | **30.12** | ✅ **MET** |
| AUROC | > 0.75 | **0.862** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.47** | 🟡 **CLOSE** |
| S1 Accuracy | → 40% | **25.1%** | ❌ **MISSING** |

**3/5 targets met.** S1 accuracy significantly below target, diffusion loss needs ~0.5 reduction.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, PPL 1.46 | WikiText-103 PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08% | WikiText PPL 29.07  
**Current v2 AR PPL (30.12) competitive with GPT-2 baseline (29.07)**

## Infrastructure
**Current session:** 15.9hrs uptime, $7.19 spent | **13 spot sessions total** | **5 reclaims** (38% reclaim rate) | Total cost: **$26.20** vs $60.13 on-demand (**57% savings**)

Recent stability: Current session longest-running (15.9hrs), no recent reclaims since Mar 6 01:33 UTC.

## What's Next
After 9k remaining steps (~12.5hrs): Full v2 benchmarks (LAMBADA, WikiText-103), head-to-head v1 vs v2 comparison, confidence calibration analysis. **Priority: investigate S1 accuracy instability** - peaked at 30.7% but regressed to 25%.