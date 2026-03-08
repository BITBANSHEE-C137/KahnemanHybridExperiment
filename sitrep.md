# v3 Training SITREP

## v3 Training Status
**TRAINING NOT STARTED** - Step 0/50k (0%). GPU idle at 27°C, VRAM 4.3GB/23GB used. No rate/ETA available. Current spot: **$0.46/hr** (62% savings vs $1.21 on-demand).

## Eval Metrics & Trends
**No v3 data yet.** Historical trajectory shows v2 completion:

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 43k  | 29.96  | 3.93     | 29.2%  | 0.868 | 0.020 |
| 48k  | 29.72  | 4.73     | 21.9%  | 0.858 | 0.012 |
| 50k  | **29.65** | **4.70** | **22.0%** | **0.863** | **0.009** |

**Trends:** AR PPL stable ~29.7. Diff loss volatile 3.9-4.7. S1 accuracy degraded 29%→22%. AUROC steady ~0.86. **ECE improved** 0.020→0.009.

## Target Scorecard
| Metric | Target | v2 Final | Status |
|--------|--------|----------|---------|
| AR PPL | < 40 | **29.65** | ✅ **MET** |
| AUROC | > 0.75 | **0.863** | ✅ **MET** |
| ECE | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.70** | ❌ **17% high** |
| S1 Acc | → 40% | **22.0%** | ❌ **45% short** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText-103 PPL 43.86, S1 loss 4.12. **v2 shows:** AR improved 43.86→29.65 PPL (-33%), but S1 accuracy remains concerning at 22% vs 40% target.

## Infrastructure
**SPOT INSTABILITY:** 5 sessions, 4 reclaims in <2hrs. Total cost **$0.29**. Current instance up 6.7min. Pattern shows ~8min avg uptime before reclaim in us-east-1a.

**CRITICAL:** Frequent spot reclaims preventing training start. Consider reserved capacity or different AZ.

## What's Next
**IMMEDIATE:** Resolve spot stability or v3 won't progress. Once stable: begin 50k step training, target S1 accuracy improvement and diffusion loss convergence to 4.0.