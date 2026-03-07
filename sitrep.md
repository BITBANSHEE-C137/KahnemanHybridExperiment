# v2 Training SITREP

## v2 Training Status
**Step 46,500/50,000 (93% complete)** | A10G @ 100% util, 197W/300W, 50°C | **16.6/23GB VRAM** used  
Rate: ~185 steps/hr | **ETA: ~19 hours** | Spot: **$0.464/hr** vs $1.212 on-demand (**61.8% savings**)

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | AUROC | ECE |
|------|--------|-----------|-------------|-------|-----|
| 39k  | 30.41  | 3.80      | 30.7%       | 0.863 | 0.007 |
| 40k  | 30.21  | **4.56**  | **23.2%**   | 0.857 | 0.007 |
| 41k  | 30.12  | 4.47      | 25.1%       | 0.862 | **0.012** |
| 42k  | 30.08  | 4.07      | 29.0%       | 0.862 | **0.016** |
| 43k  | 29.96  | 3.93      | 29.2%       | 0.868 | **0.020** |
| 44k  | 29.96  | **4.37**  | **25.4%**   | 0.865 | **0.016** |
| 45k  | 29.80  | 3.86      | 29.3%       | **0.875** | **0.016** |
| 46k  | **29.74** | 4.15   | **26.2%**   | 0.865 | **0.011** |

**Trends**: AR PPL steadily improving ✓. Diffusion loss volatile (3.8→4.6→4.2). S1 accuracy unstable, regressing from 30% peak. AUROC solid but ECE degrading from initial 0.007 to 0.011-0.020 range.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.74** | ✅ **Met** |
| AUROC | > 0.75 | **0.865** | ✅ **Met** |
| ECE | < 0.05 | **0.011** | ✅ **Met** |
| Diff Loss | → 4.0 | **4.15** | ⚠️ **Close** |
| S1 Accuracy | → 40% | **26.2%** | ❌ **Miss** |

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v2 AR performance superior to v1 (29.74 vs 43.86 PPL)**. S1 accuracy concerning at 26% vs v1's implied ~67% improvement.

## Infrastructure
**15 spot instances, 14 reclaims** over 3 days | Current: 6.8hr uptime on g5.2xlarge  
Total cost: **$29.44** (vs $43.81 on-demand) | **Current session stable** - no recent reclaims  
Checkpoint sync active, last backup: step_46000.pt (1.5GB)

## What's Next
3.5k steps remaining (~19hrs). **Critical**: Monitor S1 accuracy regression and ECE calibration drift. Post-completion: v2 benchmarks vs v1/GPT-2, confidence head analysis for calibration issues, diffusion loss convergence assessment.