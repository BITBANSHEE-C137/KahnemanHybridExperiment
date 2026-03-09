# v3 Training SITREP

## v3 Training Status
**Step 20,400/50,000 (40.8% complete)** | A10G @ 100% util, 198W/300W, 57°C | VRAM: 16.6/23GB  
Rate: ~12 steps/min | **ETA: ~41h** | Spot: $0.48/hr (61% savings) | Current session: 41min uptime

## Eval Metrics & Trends

| Step  | AR PPL | Diff Loss | S1 Tok Acc | Conf AUROC | Conf ECE |
|-------|--------|-----------|-------------|------------|----------|
| 13000 | 28.41  | 4.424     | 24.1%       | 0.844      | 0.011    |
| 14000 | 28.51  | 4.291     | 24.7%       | 0.852      | 0.009    |
| 15000 | 28.64  | 4.496     | 23.7%       | **0.864**  | **0.005**|
| 16000 | 28.66  | 4.383     | 23.5%       | 0.856      | 0.010    |
| 17000 | 28.89  | 4.344     | 25.2%       | 0.858      | 0.008    |
| 18000 | 28.99  | 4.439     | 23.0%       | 0.858      | 0.010    |
| 19000 | 29.21  | 4.389     | 22.1%       | 0.866      | 0.011    |
| 20000 | 29.22  | 4.235     | **26.8%**   | 0.857      | 0.005    |

**Concerning AR PPL drift upward** (+0.8 since step 13k). S1 accuracy volatile but trending down. AUROC stable ~0.86, ECE excellent <0.01.

## Target Scorecard
| Metric | Target | Current | Status |
|--------|--------|---------|---------|
| AR PPL | < 40 | **29.2** | ✅ |
| AUROC | > 0.75 | **0.857** | ✅ |
| ECE | < 0.05 | **0.005** | ✅ |
| Diff Loss | → 4.0 | **4.24** | 🔄 |
| S1 Accuracy | → 40% | **26.8%** | ❌ |

**3/5 targets met.** Diffusion loss improving (4.42→4.24). S1 accuracy well below target.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26%/1.46 PPL, WikiText-103 43.86 PPL, S1 loss 4.12  
GPT-2 baseline: LAMBADA 95.08%, WikiText 29.07 PPL  
Current v3 AR PPL (**29.2**) significantly better than v1 (43.86), approaching GPT-2 baseline.

## Infrastructure
**18 spot reclaims** in 2 days - severe instability. Multiple micro-sessions <1hr. Current g5.2xlarge stable 41min.  
Total cost: **$17.45** (projected $17.35 this session). 61% savings vs on-demand.  
Checkpoint sync active, last: step_20000.pt (1.5GB).

## What's Next
**Critical:** Address spot instability - consider reserved capacity or higher bid. AR PPL regression needs investigation. S1 accuracy severely underperforming - may need architecture/hyperparameter changes. Next eval due ~step 21k.