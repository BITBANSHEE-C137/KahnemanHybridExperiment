# v2 Training Status

**Step 41,900/50,000 (83.8% complete)** | A10G @ 100% util, 192W/300W, 50°C | **Steps/hr: ~370** | ETA: **~22 hours** | Spot rate: **$0.463/hr** (61.8% savings)

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|-------------|------------|----------|
| 34000 | 31.13  | 4.68      | 22.0%       | 0.854      | 0.0086   |
| 35000 | 30.84  | 4.79      | 21.4%       | 0.855      | 0.0109   |
| 36000 | 30.69  | **4.30**  | **24.8%**   | 0.863      | 0.0100   |
| 37000 | 30.65  | 4.75      | 21.6%       | 0.861      | **0.0069** |
| 38000 | 30.44  | **4.28**  | **26.7%**   | 0.865      | **0.0042** |
| 39000 | 30.41  | **3.80**  | **30.7%**   | 0.863      | 0.0068   |
| 40000 | 30.21  | 4.56      | 23.2%       | 0.857      | 0.0072   |
| 41000 | **30.12** | 4.47   | 25.1%       | 0.862      | 0.0123   |

**Trends:** AR PPL steadily improving ✓ | Diffusion loss volatile but trending down | S1 accuracy peaked at 39k, now fluctuating | AUROC stable ~0.86 | ECE excellent <0.02

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **30.12** | ✅ **Met** |
| Conf AUROC | > 0.75 | **0.862** | ✅ **Met** |
| Conf ECE | < 0.05 | **0.012** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.47** | 🔶 **Close** |
| S1 Accuracy | → 40% | **25.1%** | ❌ **Gap** |

## v1 Benchmark Baseline

v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07

**v2 vs v1:** AR performance tracking ahead of v1 (30.12 vs 43.86 PPL). S1 accuracy volatile but improving trajectory.

## Infrastructure

**Total cost: $26.89** across 15 sessions | Current session: 1.3hr uptime, $0.56 cost | **14 spot reclaims** - high churn but stable recovery | Most interruptions during peak hours

## What's Next

After v2 completes (~22h): Run v2 benchmarks on LAMBADA/WikiText | Compare v1→v2 joint training effects | **Priority:** Analyze S1 accuracy volatility and confidence calibration trends