# Experiment Data

Raw training data exported from this experiment for transparency and reproducibility.

## Files

| File | Description | Source |
|------|-------------|--------|
| `eval_metrics.csv` | Checkpoint evaluation metrics (every 1,000 steps) | `eval_metrics/*.json` |
| `training_steps.csv` | Step-level training losses and learning rate (every 100 steps) | W&B output logs |
| `export_wandb.py` | Script to re-export full history from W&B API | — |

## Eval Metrics Columns

| Column | Description |
|--------|-------------|
| `step` | Training step |
| `ar_perplexity` | Autoregressive perplexity (System 2) |
| `diff_loss` | Diffusion cross-entropy loss (System 1) |
| `s1_token_accuracy` | Fraction of masked tokens correctly predicted |
| `conf_accuracy` | Binary accuracy of confidence head |
| `conf_ece` | Expected Calibration Error |
| `conf_auroc` | Area Under ROC Curve |

## Training Steps Columns

| Column | Description |
|--------|-------------|
| `step` | Training step |
| `ar_loss` | Autoregressive cross-entropy loss |
| `diff_loss` | Diffusion cross-entropy loss |
| `conf_accuracy` | Confidence head accuracy (updated at eval steps) |
| `learning_rate` | Current learning rate |

## W&B Project

The full training history is logged to Weights & Biases:
**[wandb.ai/bitbanshee-c137/dual-process-lm](https://wandb.ai/bitbanshee-c137/dual-process-lm)**

To re-export all W&B data:
```bash
pip install wandb
wandb login
python experiments/export_wandb.py
```
