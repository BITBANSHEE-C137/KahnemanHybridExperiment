# v2 Training SITREP

## v2 Training Status
**Step 25,900 / 50,000 (51.8%)** | GPU: **98%** util, 201W/300W, 50°C | Rate: ~11.6 steps/min | **ETA: ~35 hours** | Spot cost: **$0.45/hr** (63% savings) | Total spend: **$17.56**

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 18000 | 30.77 | 4.03 | 27.2% | 0.869 | 0.006 |
| 19000 | 30.81 | 4.31 | 24.5% | 0.860 | 0.007 |
| 20000 | 30.92 | 4.75 | 21.3% | 0.851 | 0.007 |
| 21000 | 30.88 | 4.85 | 20.7% | 0.851 | 0.007 |
| 22000 | 30.95 | 4.19 | 27.5% | 0.858 | 0.010 |
| 23000 | 31.03 | 4.03 | 27.9% | 0.864 | 0.010 |
| 24000 | 30.98 | 4.46 | 24.3% | 0.863 | 0.005 |
| **25000** | **31.22** | **4.20** | **27.6%** | **0.860** | **0.012** |

**Trends**: AR PPL stable ~31 (good). **Diff loss volatile** - spiked to 4.85 then recovered. S1 accuracy **unstable** (20-28% range). AUROC steady ~0.86. ECE **degraded** from 0.006 → 0.012.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **31.22** | ✅ **MET** |
| AUROC | > 0.75 | **0.860** | ✅ **MET** |
| ECE | < 0.05 | **0.012** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.20** | 🟡 **CLOSE** |
| S1 Accuracy | → 40% | **27.6%** | ❌ **MISS** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. **v2 AR already superior** to v1 (31.2 vs 43.9 PPL). S1 accuracy concerning - need 45% improvement to match v1's implied performance.

## Infrastructure
**12 spot sessions**, **63% cost savings** vs on-demand. Current: g5.2xlarge us-east-1a, **2.4h uptime**. Recent stability good - no reclaims since step 24k. Total **12 interruptions** but checkpoint recovery working well.

## What's Next
Training **49% complete** - expect completion ~March 7. Priority: **monitor S1 accuracy volatility** and diffusion loss stability. Post-completion: comprehensive v1/v2 benchmarks, confidence calibration analysis, S1 token prediction deep-dive.