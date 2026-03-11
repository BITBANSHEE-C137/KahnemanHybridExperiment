# v3 Training SITREP - Step 43.5k

## v3 Training Status
**Step:** 43,500/50,000 (**87%** complete)  
**GPU:** L4 @ **98%** util, 74W power, 81°C, 16.6GB VRAM used  
**Rate:** ~300 steps/hr | **ETA:** ~22 hours  
**Spot Cost:** $0.43/hr (**56.5% savings**) | Total: $34.97 across 21 sessions

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|------|--------|-----------|-------------|------------|----------|
| 36k  | 28.59  | 4.46      | 23.5%       | 0.864      | 0.0109   |
| 38k  | 28.43  | 4.02      | 28.5%       | 0.864      | 0.0092   |
| 40k  | 28.27  | 3.76      | 30.3%       | **0.881**  | 0.0094   |
| 42k  | 28.33  | 3.89      | 29.1%       | 0.870      | 0.0126   |
| 43k  | **28.14** | **4.20** | **25.9%**  | 0.869      | **0.0103** |

**Trends:** AR PPL improving steadily. **Diffusion loss volatile** - dropped to 3.76 then spiked to 4.20. **S1 accuracy regressing** from 30% peak. AUROC stable ~0.87.

## Target Scorecard
| Target | Current | Status |
|--------|---------|--------|
| AR PPL < 40 | **28.14** | ✅ **PASS** |
| AUROC > 0.75 | **0.869** | ✅ **PASS** |  
| ECE < 0.05 | **0.0103** | ✅ **PASS** |
| Diff loss → 4.0 | **4.20** | ⚠️ **CLOSE** |
| S1 accuracy → 40% | **25.9%** | ❌ **BEHIND** |

**3/5 targets met.** S1 accuracy **concerning** - peaked at 30% then dropped 4pp.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v3 AR performance stronger than v1** (28.14 vs 43.86 PPL)

## Infrastructure
**Uptime:** 6.1hrs current session, 21 total sessions  
**Spot stability:** No recent reclaims, $0.43/hr rate stable  
**Checkpoints:** 41k/42k/43k synced (1.5GB each)  
**Status:** All systems nominal

## What's Next
**Critical:** Monitor S1 accuracy regression - may need learning rate adjustment  
After 50k: Full benchmarks vs v1, confidence calibration analysis, diffusion convergence assessment