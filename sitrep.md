## v3 Training Status
**Step 38,700 / 50,000 (77.4%)** | GPU: 100% util, 204W/300W, 57°C | VRAM: 16.6/23GB | Rate: ~3 steps/min | **ETA: 3.3 days** | Spot: $0.44/hr (63% savings) | Total cost: **$31.48**

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|---------|-----------|---------|-------|-----|
| 31000 | 28.95 | 4.47 | 23.3% | 0.871 | 0.003 |
| 32000 | 29.04 | 4.35 | 24.2% | 0.865 | 0.009 |
| 33000 | 28.93 | 4.09 | 26.6% | 0.861 | 0.009 |
| 34000 | 28.85 | 4.15 | 25.6% | 0.871 | 0.007 |
| 35000 | 28.73 | 4.26 | 25.0% | 0.863 | 0.006 |
| 36000 | 28.59 | 4.46 | 23.5% | 0.864 | 0.011 |
| 37000 | 28.51 | 4.52 | 24.1% | 0.856 | 0.006 |
| 38000 | **28.43** | **4.02** | **28.5%** | 0.864 | 0.009 |

**Trends**: AR PPL steadily improving. **S1 accuracy jump** from 24% to 28.5% at step 38k. Diff loss volatile but trending down. AUROC stable ~0.86. ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **28.43** | ✅ **Met** |
| AUROC > 0.75 | **0.864** | ✅ **Met** |
| ECE < 0.05 | **0.009** | ✅ **Met** |
| Diff loss → 4.0 | **4.02** | ✅ **Nearly met** |
| S1 accuracy → 40% | **28.5%** | ❌ 11.5% gap |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**Current v3 shows strong AR performance** (PPL 28.43 vs v1's 43.86). S1 accuracy at 28.5% suggests continued progress toward joint training effectiveness.

## Infrastructure
**Current**: g5.2xlarge us-east-1f, 1hr uptime, $0.46 accumulated
**History**: 20 sessions, **12 spot interruptions** (brutal). Major stability on sessions 2 (23hr) and 19 (24hr). Multiple instance types tested due to availability.
**Cost efficiency**: 63% savings vs on-demand

## What's Next
**T-minus 11,300 steps**: S1 accuracy needs 11.5% boost to hit 40% target. Monitor for continued improvement trend from step 38k jump. Post-completion: full benchmark suite, v1 vs v3 comparison, confidence calibration analysis.