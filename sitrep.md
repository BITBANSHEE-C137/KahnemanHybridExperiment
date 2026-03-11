# ML Ops SITREP - v3 Training

## v3 Training Status
**Step 37,200/50,000 (74.4% complete)** | **ETA: ~16 hours**
- GPU: L4 at **100% util**, 70.6W/72W, 80°C, 16.6/23GB VRAM
- Rate: ~290 steps/hour | Spot: **$0.46/hr** (53% savings vs on-demand)
- Current session: 22.5hrs uptime, stable

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 30k  | 29.16  | 4.34      | 24.6%  | 0.868 | 0.0046 |
| 33k  | 28.93  | **4.09**  | **26.6%** | 0.861 | 0.0086 |
| 35k  | 28.73  | 4.26      | 25.0%  | 0.863 | 0.0057 |
| 37k  | **28.51** | 4.52   | 24.1%  | 0.856 | **0.0065** |

**Trends:** AR PPL improving steadily (-2.3%). Diffusion loss volatile, **+10% regression** from 33k low. S1 accuracy plateaued ~24-26%. AUROC declining slightly (-1.4%). ECE well-controlled.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.51** | ✅ **MET** |
| AUROC > 0.75 | **0.856** | ✅ **MET** |
| ECE < 0.05 | **0.0065** | ✅ **MET** |
| Diff Loss → 4.0 | **4.52** | ❌ **12.5% over** |
| S1 Acc → 40% | **24.1%** | ❌ **40% below** |

**3/5 targets met.** S1 performance significantly lagging. Diffusion loss regressed from step 33k optimum.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12
Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07

**Current AR performance superior to v1** (28.51 vs 43.86 PPL). S1 loss tracking toward v1 levels.

## Infrastructure
**Total cost: $30.36** across 19 sessions | **Current L4 session: $10.33**
- Major interruption period: 3/9 evening (11 failed restarts, step ~20k)
- Stable since 3/10 04:25 UTC on current g6.2xlarge
- Checkpoints: steps 35k/36k/37k synced, 1.5GB each

## What's Next
- **Monitor diffusion loss regression** - consider LR adjustment if trend continues
- S1 accuracy plateau concerning - may need architecture review
- Target completion: 3/11 ~19:00 UTC at current rate
- Post-completion: comprehensive v1 vs v3 benchmark comparison, confidence calibration analysis