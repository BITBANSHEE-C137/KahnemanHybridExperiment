# v2 Training Status

**TRAINING INTERRUPTED** - Current step: **0/50k** (0.0%). Last checkpoint: **step_24000** from 19:46 UTC.

GPU: A10G @ **99% util**, 201W/300W, 53°C, 16.6GB/23GB VRAM. Instance restarted at 19:52 UTC, **training not resumed**.

Spot rate: **$0.448/hr** (63% savings), current session cost: $0.10. **ETA: Unknown** - trainer stalled.

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE    |
|-------|--------|-----------|--------|-------|--------|
| 17000 | 30.70  | 4.52      | 23.7%  | 0.860 | 0.0074 |
| 18000 | 30.77  | **4.03**  | **27.2%** | **0.869** | **0.0060** |
| 19000 | 30.81  | 4.31      | 24.5%  | 0.860 | 0.0073 |
| 20000 | 30.92  | 4.75      | 21.3%  | 0.851 | 0.0072 |
| 21000 | 30.88  | 4.85      | 20.7%  | 0.851 | 0.0075 |
| 22000 | 30.95  | 4.19      | 27.5%  | 0.858 | **0.0096** |
| 23000 | 31.03  | **4.03**  | **27.9%** | 0.864 | **0.0095** |
| 24000 | 30.98  | 4.46      | 24.3%  | 0.863 | 0.0050 |

**Concerning trends**: AR PPL **regressing** (30.70→30.98), diffusion loss **volatile** (4.03→4.85→4.03→4.46). S1 accuracy **inconsistent** but peaked at 27.9%. AUROC stable ~0.86. ECE degraded to 0.0095.

## Target Scorecard

| Target | Current | Status |
|--------|---------|---------|
| AR PPL < 40 | **30.98** | ✅ **MET** |
| AUROC > 0.75 | **0.863** | ✅ **MET** |
| ECE < 0.05 | **0.0050** | ✅ **MET** |
| Diff Loss → 4.0 | **4.46** | 🔶 **CLOSE** |
| S1 Acc → 40% | **24.3%** | ❌ **MISS** (60% of target) |

**3/5 targets met**. S1 accuracy **significantly behind** target.

## v1 Benchmark Baseline

v1 (step 50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12.  
Pretrained GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL.

v2 shows **better S1 performance** (4.46 vs 4.12 loss) but **worse AR** (30.98 vs v1's implied ~29 PPL).

## Infrastructure

**12 spot reclaims** in 2 days. Total cost: **$16.53**. Current session: 12min uptime, no training progress.

**Critical**: Trainer not resuming from checkpoint. Sync running but **training stalled**.

## What's Next

**IMMEDIATE**: Debug trainer restart failure. Resume from step_24000.pt checkpoint.

Post-completion: v2 benchmarks vs v1, analyze confidence head regression at steps 22k-23k, investigate S1 accuracy volatility pattern.