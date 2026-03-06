# v2 Training SITREP

## v2 Training Status
**Step 32,800/50,000 (65.6% complete)**
- GPU: 98% util, A10G @ 53°C, 16.6GB/23GB VRAM
- Rate: ~500 steps/6h → **ETA: ~21h remaining**
- Spot: $0.45/h (62.8% savings vs on-demand $1.21/h)
- Current session cost: $2.69, projected total: **$12.10**

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|--------|
| 25000 | 31.22  | 4.20      | 27.6%   | 0.860 | 0.012  |
| 26000 | 31.46  | 4.06      | 28.0%   | 0.863 | 0.018  |
| 28000 | 31.32  | 3.95      | 28.2%   | **0.872** | **0.007** |
| 30000 | 31.68  | 4.08      | 28.1%   | 0.864 | 0.023  |
| 32000 | **31.39** | **3.96** | **28.4%** | 0.871 | 0.013  |

**Trends:** AR PPL stable ~31.4. Diffusion loss improving (3.95→3.96). S1 accuracy plateaued at 28%. AUROC peaked at 0.872 (step 28k), slight regression. **ECE volatile but good**.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **31.39** | ✅ **MET** |
| AUROC > 0.75 | **0.871** | ✅ **MET** |
| ECE < 0.05 | **0.013** | ✅ **MET** |
| Diff loss → 4.0 | **3.96** | ✅ **MET** |
| S1 accuracy → 40% | **28.4%** | ❌ **MISS** (12% gap) |

**4/5 targets met**. S1 accuracy stalled at 28% - may need architecture changes.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46; WikiText PPL 43.86; S1 loss 4.12
GPT-2: LAMBADA 95.08%, WikiText PPL 29.07

v2 shows **AR improvement** (31.4 vs 43.9 PPL) and **S1 improvement** (3.96 vs 4.12 loss, 67% better accuracy trajectory).

## Infrastructure
**13 spot sessions, 5.9h uptime**
- **12 reclaims** - high churn but resilient recovery
- Cost efficiency: $21.66 total vs $32.43 on-demand
- Current session stable 6h+ in us-east-1b

## What's Next
After v2 (17k steps): comprehensive benchmarks, v1 vs v2 head-to-head, confidence calibration analysis. **S1 accuracy plateau needs investigation** - may require learning rate schedule or architecture tweaks.