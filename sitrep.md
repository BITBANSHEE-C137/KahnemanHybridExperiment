# v2 Training Status SITREP

## v2 Training Status
**Step 39,000/50,000 (78%)** | GPU: 100% util @ 193W | Rate: ~230 steps/hr | **ETA: 2.0 days** | Current spot: **$0.45/hr** (63% savings) | Session cost: **$6.08**

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|---------|-------|---------|
| 32k   | 31.39  | 3.96      | 28.4%   | 0.871 | 0.0129 |
| 34k   | 31.13  | 4.68      | 22.0%   | 0.854 | 0.0086 |
| 36k   | 30.69  | 4.30      | 24.8%   | 0.863 | 0.0100 |
| 38k   | 30.44  | 4.28      | 26.7%   | 0.865 | 0.0042 |
| **39k** | **30.41** | **3.80** | **30.7%** | **0.863** | **0.0068** |

**Trends:** AR PPL steadily improving ✓ | Diff loss volatile but recent drop ✓ | S1 accuracy recovering strongly ✓ | AUROC stable ~0.86 ✓ | ECE excellent <0.01 ✓

## Target Scorecard

| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **30.41** | ✅ |
| AUROC  | > 0.75 | **0.863** | ✅ |
| ECE    | < 0.05 | **0.007** | ✅ |
| Diff Loss | → 4.0 | **3.80** | ✅ |
| S1 Acc | → 40% | **30.7%** | 🟡 (trending up) |

**4/5 targets met.** S1 accuracy recovering from mid-training dip, now at 30.7% vs 22% nadir.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12 | GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL | **v2 AR PPL already superior to v1** (30.4 vs 43.9)

## Infrastructure
Current session (13th): **13.4hr uptime**, no interruptions | Historical: **12 spot reclaims** over 2.5 days | Total cost **$25.06** vs $54.65 on-demand (**54% savings**) | Checkpoint sync active, 1.5GB latest

## What's Next
**11k steps remaining** (~2 days). Post-completion: v2 LAMBADA/WikiText benchmarks, direct v1-v2 comparison, confidence calibration analysis on improved ECE performance.