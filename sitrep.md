# v2 Training SITREP

## v2 Training Status
**Progress:** 29,400/50,000 steps (**58.8%** complete)
- **GPU:** A10G at 100% util, 197W/300W, 53°C, 16.6/23GB VRAM
- **Rate:** ~1.7 hr remaining at current pace
- **ETA:** ~2026-03-06 05:00 UTC
- **Spot Cost:** $0.45/hr (**62.9% savings**), $19.85 total

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|--------|-------|-------|
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | 0.010 |
| 23000 | 31.03  | 4.03      | 27.9%  | 0.864 | 0.010 |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.005 |
| 25000 | 31.22  | 4.20      | 27.6%  | 0.860 | 0.012 |
| 26000 | 31.46  | 4.06      | 28.0%  | 0.863 | 0.018 |
| 27000 | 31.46  | 4.48      | 24.4%  | 0.862 | 0.009 |
| 28000 | 31.32  | 3.95      | 28.2%  | **0.872** | 0.007 |
| 29000 | **31.43** | **4.21** | **27.7%** | **0.860** | **0.022** |

**Trends:** AR PPL plateaued ~31.4. Diffusion loss volatile (3.95→4.21). **AUROC regression** from 0.872→0.860. **ECE spike** to 0.022.

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **31.43** | ✅ |
| AUROC  | > 0.75 | **0.860** | ✅ |
| ECE    | < 0.05 | **0.022** | ✅ |
| Diff Loss | → 4.0 | **4.21** | ❌ |
| S1 Acc | → 40% | **27.7%** | ❌ |

**3/5 targets met.** Diffusion loss needs **5%** improvement, S1 accuracy **44%** behind.

## v1 Benchmark Baseline
- **LAMBADA:** 94.26% acc, 1.46 PPL
- **WikiText-103:** 43.86 PPL  
- **S1 loss:** 4.12 (67% improvement from pretraining)
- **GPT-2 baseline:** 95.08% LAMBADA, 29.07 WikiText PPL

v1 showed slight AR regression but major S1 gains from joint training.

## Infrastructure
**Spot History:** 13 sessions, **$19.85** total cost vs $32.46 on-demand
- Current session: 1.9hrs uptime, stable in us-east-1b
- **High reclaim rate:** 12 interruptions, avg session 2.6hrs
- Recent stability improving (4.4hrs last session)

## What's Next
**Post v2 completion (~2hrs):**
1. Full benchmark suite (LAMBADA, WikiText-103, HellaSwag)
2. v1 vs v2 head-to-head comparison
3. Confidence calibration analysis on ECE regression
4. Diffusion sampling quality assessment

**Priority:** Address ECE degradation and diffusion loss plateau.