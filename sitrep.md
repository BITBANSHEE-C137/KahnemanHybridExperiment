# v2 Training SITREP

## v2 Training Status
**Step 38,500/50,000** (77% complete). A10G at **100% util**, 191W/300W, 53°C. Current rate ~300 steps/hr. **ETA: ~39 hours**. Spot rate $0.45/hr (**62.7% savings** vs on-demand). No interruptions in current 13hr session.

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 31000| 31.60  | 4.49      | 24.5%  | 0.862 | 0.014 |
| 32000| 31.39  | 3.96      | 28.4%  | 0.871 | 0.013 |
| 33000| 31.29  | 4.23      | 25.4%  | 0.864 | 0.008 |
| 34000| 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 35000| 30.84  | 4.79      | 21.4%  | 0.855 | 0.011 |
| 36000| 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 37000| 30.65  | 4.75      | 21.6%  | 0.861 | 0.007 |
| **38000**| **30.44** | **4.28** | **26.7%** | **0.865** | **0.004** |

**Trends:** AR PPL **steadily improving** (-3.7% over 7k steps). S1 accuracy **volatile but recovering**. AUROC **stable ~0.86**. ECE **excellent convergence** to 0.004. Diff loss **unstable**, oscillating 3.96-4.79.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|--------|
| AR PPL | < 40 | **30.44** | ✅ **MET** |
| AUROC | > 0.75 | **0.865** | ✅ **MET** |
| ECE | < 0.05 | **0.004** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.28** | 🟡 Close |
| S1 Accuracy | → 40% | **26.7%** | ❌ **Gap: -13.3%** |

**3/5 targets met.** S1 accuracy **major gap** - needs +50% improvement.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12. GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL. **Current v2 AR PPL (30.44) competitive with WikiText baseline.** S1 performance unknown until benchmarking.

## Infrastructure
**13 spot sessions, 12 interruptions** across us-east-1a/b/f. Total cost **$24.83** (**62.7% savings**). Current session: 13hrs uptime, no issues. Instance hopping pattern suggests **high spot pressure** - consider reserved capacity for final 12k steps.

## What's Next
12k steps remaining (~39hrs). **Critical:** Monitor S1 accuracy - may need hyperparameter adjustment if no improvement. Post-completion: comprehensive v2 benchmarks, confidence head analysis, v1 vs v2 head-to-head on LAMBADA/WikiText.