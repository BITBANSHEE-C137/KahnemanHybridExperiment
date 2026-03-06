# v2 Training SITREP

## v2 Training Status
**Step 42,700/50,000 (85.4%)** | GPU: 98% util, 191W/300W, 50°C | Rate: ~400 steps/hr | **ETA: ~18hrs** | Current spot: $0.46/hr (61.8% savings) | Session cost: $1.06

## Eval Metrics & Trends

| Step | AR PPL | AUROC | ECE | Diff Loss | S1 Acc |
|------|--------|-------|-----|-----------|---------|
| 35k  | 30.84  | 0.855 | 0.011 | 4.789     | 21.4%   |
| 38k  | 30.44  | 0.865 | 0.004 | 4.275     | 26.7%   |
| 39k  | 30.41  | 0.863 | 0.007 | 3.795     | 30.7%   |
| **42k** | **30.08** | **0.862** | **0.016** | **4.073** | **29.0%** |

**Trends:** AR PPL steadily improving. AUROC stable ~0.86. **ECE degrading** (0.004→0.016). Diff loss volatile but trending down. S1 accuracy peaked at 39k, slight regression.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | <40 | **30.08** | ✅ **MET** |
| AUROC | >0.75 | **0.862** | ✅ **MET** |
| ECE | <0.05 | **0.016** | ✅ **MET** |
| Diff Loss | →4.0 | **4.073** | ⚠️ **CLOSE** |
| S1 Accuracy | →40% | **29.0%** | ❌ **BEHIND** |

**3/5 targets met.** S1 accuracy stalled ~10pts below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/PPL 1.46, WikiText PPL 43.86, S1 loss 4.12. Pretrained GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. 

**v2 AR performance superior** (30.08 vs 43.86 PPL). S1 accuracy conversion pending but diffusion loss comparable to v1.

## Infrastructure
**15 spot sessions**, $27.40 total cost. Current session stable 2.3hrs, no reclaims. **Aggressive spot hopping** across AZs (1a→1b→1f). Historical reclaim rate ~12hrs avg session length. Storage: 1.5GB checkpoints, sync running.

## What's Next
7.3k steps remaining (~18hrs). **Priority: S1 accuracy improvement** - consider LR adjustment if stagnant. Post-completion: v2 benchmarks on LAMBADA/WikiText, v1-v2 head-to-head comparison, confidence calibration analysis on ECE regression.