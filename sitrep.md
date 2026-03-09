# v3 Training SITREP

## v3 Training Status
**Step 19,300/50,000 (38.6% complete)** | GPU util: **99%** L4 @ 82°C | Rate: ~10.5 steps/min | **ETA: ~49hrs** | Spot rate: **$0.37/hr** (54% savings vs on-demand)

## Eval Metrics & Trends
| Step  | AR PPL | Diff Loss | S1 Acc | AUROC | ECE   |
|-------|--------|-----------|---------|-------|-------|
| 12000 | 28.12  | 4.309     | 25.0%   | 0.853 | 0.007 |
| 13000 | 28.41  | 4.424     | 24.1%   | 0.844 | 0.011 |
| 14000 | 28.51  | 4.291     | 24.7%   | 0.852 | 0.009 |
| 15000 | 28.64  | 4.496     | 23.7%   | 0.864 | 0.005 |
| 16000 | 28.66  | 4.383     | 23.5%   | 0.856 | 0.010 |
| 17000 | 28.89  | 4.344     | 25.2%   | 0.858 | 0.008 |
| 18000 | 28.99  | 4.439     | 23.0%   | 0.858 | 0.010 |
| 19000 | 29.21  | 4.389     | 22.1%   | 0.866 | 0.011 |

**🔴 Concerning trends:** AR PPL degrading (+3.9% since step 12k), S1 accuracy declining (-11.6%). Diffusion loss volatile but stable. AUROC holding strong.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40   | **29.2** | ✅ |
| AUROC  | > 0.75 | **0.866** | ✅ |
| ECE    | < 0.05 | **0.011** | ✅ |
| Diff Loss | → 4.0 | **4.39** | 🟡 |
| S1 Acc | → 40% | **22.1%** | 🔴 |

**3/5 targets met.** S1 accuracy severely underperforming vs v1 baseline.

## v1 Benchmark Baseline
v1 (step 50k): LAMBADA 94.26%, PPL 1.46 | WikiText PPL 43.86 | S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText PPL 29.07  
**Current v3 AR performance on-track** but S1 process significantly weaker than v1.

## Infrastructure
**Current:** g6.xlarge spot (39min uptime) | **Total sessions:** 3 instances  
**Cost:** $14.05 spent, $19.36 projected | **Uptime:** 99.2% (1 reclaim event)  
Previous g5.2xlarge terminated after 23.5hrs - normal spot behavior.

## What's Next
**Immediate:** Monitor S1 accuracy decline - may need architecture review if trend continues. Eval checkpoint at 20k due.  
**Post-v3:** Full benchmark suite, confidence calibration analysis, v1→v3 dual-process evolution study.