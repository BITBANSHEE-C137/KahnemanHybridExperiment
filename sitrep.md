# v2 Training SITREP

## v2 Training Status
**43,600 / 50,000 steps (87.2%)**  
GPU: **99.0% util**, A10G @ 193W/300W, 50°C, 16.6GB/23GB VRAM  
Rate: ~400 steps/hour | **ETA: 16 hours**  
Spot cost: **$0.46/hr** (61.8% savings vs $1.21 on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 36000 | 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 39000 | 30.41  | **3.80**  | **30.7%** | 0.863 | 0.007 |
| 42000 | 30.08  | 4.07      | 29.0%  | 0.862 | 0.016 |
| 43000 | **29.96** | **3.93** | 29.2% | **0.868** | **0.020** |

**Trends:** AR PPL steadily improving. Diff loss volatile but trending down. S1 accuracy peaked at 39k then plateaued. **ECE degrading** - confidence calibration worsening.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **29.96** | ✅ **MET** |
| AUROC > 0.75 | **0.868** | ✅ **MET** |
| ECE < 0.05 | **0.020** | ✅ **MET** |
| Diff loss → 4.0 | **3.93** | ✅ **MET** |
| S1 accuracy → 40% | **29.2%** | ❌ **MISS** |

**4/5 targets met.** S1 accuracy stalled ~10% below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v2 AR PPL (29.96) matches GPT-2 baseline** - joint training maintained AR performance.

## Infrastructure
Current session: 3.3h uptime, $1.49 spent  
**15 spot sessions**, 8 reclaims, **$27.82 total cost**  
Most stable: 16h session (steps 28k-41k), $7.23  
Recent stability good - current instance running 3+ hours

## What's Next
6.4k steps remaining (~16h). Post-completion: v2 benchmarks vs v1/GPT-2, analyze confidence head degradation, investigate S1 accuracy plateau. **ECE trend concerning** - may need confidence recalibration.