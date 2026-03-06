# ML Ops SITREP - v2 Dual Process Training

## v2 Training Status
**Step 34,400 / 50,000 (68.8%)** | A10G @ 100% util, 193W/300W, 51°C | Rate: ~1.23 steps/sec | **ETA: ~3.5hrs** | Current spot: $0.45/hr (62.7% savings) | Session cost: $3.59

## Eval Metrics & Trends
| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|---------|-------|-----|
| 27k  | 31.46  | 4.48      | 0.244   | 0.862 | 0.0095 |
| 28k  | 31.32  | **3.95**  | **0.282** | **0.872** | **0.0073** |
| 29k  | 31.43  | 4.21      | 0.277   | 0.860 | 0.0217 |
| 30k  | 31.68  | 4.08      | 0.281   | 0.864 | 0.0234 |
| 31k  | 31.60  | 4.49      | 0.245   | 0.862 | 0.0141 |
| 32k  | 31.39  | 3.96      | 0.284   | 0.871 | 0.0129 |
| 33k  | 31.29  | 4.23      | 0.254   | 0.864 | **0.0075** |
| 34k  | **31.13** | 4.68   | 0.221   | 0.854 | 0.0086 |

**Trends:** AR PPL steadily improving ✓. **S1 accuracy regressing** (0.284→0.221), **diffusion loss volatile** (3.95→4.68). AUROC/ECE stable but below peak.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40   | **31.13** | ✅ **MET** |
| AUROC  | > 0.75 | **0.854** | ✅ **MET** |
| ECE    | < 0.05 | **0.009** | ✅ **MET** |
| Diff Loss | → 4.0 | **4.68** | ⚠️ **ABOVE TARGET** |
| S1 Accuracy | → 40% | **22.1%** | ❌ **BELOW TARGET** |

**3/5 targets met.** S1 head struggling, diffusion not converging to 4.0.

## v1 Benchmark Baseline
v1 (50k): LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2: LAMBADA 95.08%, WikiText 29.07 PPL  
**Current v2 AR PPL (31.13) approaching v1 WikiText performance (43.86)**

## Infrastructure
**13 spot sessions, $22.57 total cost** | **62.7% savings** vs on-demand | Current uptime: 7.9hrs  
Recent interruptions: Multiple brief reclaims 3/4-3/5, now stable in us-east-1b since 3/6 01:33 UTC

## What's Next
**T+3.5hrs:** v2 completion → LAMBADA/WikiText benchmarks → v1 vs v2 comparison → **S1 confidence head deep-dive** (regression analysis) → diffusion loss investigation