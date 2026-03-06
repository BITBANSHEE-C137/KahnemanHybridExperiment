# v2 Training SITREP

## v2 Training Status
**Step 37,700 / 50,000** (75.4% complete). GPU util **98%**, A10G at 53°C. Current rate ~400 steps/hr. **ETA: ~31 hours**. Spot cost **$5.40** (62.7% savings vs on-demand). Running stable on g5.2xlarge us-east-1b.

## Eval Metrics & Trends

| Step | AR PPL | Diff Loss | S1 Acc | AUROC | ECE |
|------|--------|-----------|--------|-------|-----|
| 30k  | 31.68  | 4.08      | 28.1%  | 0.864 | 0.023 |
| 32k  | 31.39  | 3.96      | 28.4%  | **0.871** | 0.013 |
| 34k  | 31.13  | 4.68      | 22.0%  | 0.854 | 0.009 |
| 36k  | 30.69  | 4.30      | 24.8%  | 0.863 | 0.010 |
| 37k  | **30.65** | 4.75      | 21.6%  | 0.861 | **0.007** |

**AR perplexity trending down** (31.68→30.65). **ECE excellent** and improving. **S1 accuracy volatile** 28%→22%→25%→22%. Diffusion loss **unstable** around 4.0-4.8 range.

## Target Scorecard
- ✅ **AR PPL < 40**: 30.65 (PASS)  
- ✅ **AUROC > 0.75**: 0.861 (PASS)
- ✅ **ECE < 0.05**: 0.007 (PASS)
- ❌ **Diff loss → 4.0**: 4.75 (MISS - trending away)
- ❌ **S1 accuracy → 40%**: 21.6% (MISS - regressed from 28%)

**3/5 targets met**. Diffusion training **not converging properly**.

## v1 Benchmark Baseline
v1 final: LAMBADA 94.26% acc, PPL 1.46; WikiText-103 PPL 43.86; S1 loss 4.12. GPT-2: LAMBADA 95.08%, WikiText PPL 29.07. 

**v2 AR already better than v1** (30.65 vs 43.86 PPL). S1 performance **significantly worse** than v1's 67% drop target.

## Infrastructure
**13 sessions, 12 spot reclaims**. Total cost **$24.38** vs $32.53 on-demand. Current session: 12hrs uptime, stable. **Frequent interruptions** but quick recovery. Latest checkpoint: step_37000.pt (1.5GB).

## What's Next
**Diffusion component needs attention** - loss not converging to 4.0 target. S1 accuracy **significantly underperforming**. Consider learning rate adjustment for diffusion head. Complete training in ~31hrs, then full benchmark suite vs v1.