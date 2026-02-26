"""Evaluation for the dual-process language model.

Computes metrics over a held-out eval set:
  - AR perplexity (System 2)
  - Diffusion loss (System 1)
  - System 1 token accuracy
  - Confidence head accuracy
  - Confidence calibration (Expected Calibration Error)
  - Confidence AUROC
"""

import math

import torch
from torch.utils.data import DataLoader

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.model.masking import create_mask
from src.evaluation.metrics import compute_auroc


def compute_calibration_error(
    confidences: torch.Tensor,
    accuracies: torch.Tensor,
    num_bins: int = 10,
) -> float:
    """Compute Expected Calibration Error (ECE).

    Bins predicted confidence values and compares mean predicted
    confidence to actual accuracy in each bin.

    Args:
        confidences: Predicted confidence values in [0, 1], shape (N,).
        accuracies: Binary correctness labels (0 or 1), shape (N,).
        num_bins: Number of equal-width bins.

    Returns:
        ECE value between 0.0 and 1.0.
    """
    total = confidences.numel()
    if total == 0:
        return 0.0

    bin_boundaries = torch.linspace(0.0, 1.0, num_bins + 1)
    ece = 0.0

    for i in range(num_bins):
        lo, hi = bin_boundaries[i], bin_boundaries[i + 1]
        if i == num_bins - 1:
            in_bin = (confidences >= lo) & (confidences <= hi)
        else:
            in_bin = (confidences >= lo) & (confidences < hi)

        count = in_bin.sum().item()
        if count == 0:
            continue

        mean_conf = confidences[in_bin].mean().item()
        mean_acc = accuracies[in_bin].mean().item()
        ece += (count / total) * abs(mean_acc - mean_conf)

    return ece


@torch.no_grad()
def evaluate(
    model: DualProcessGPT2,
    eval_dataloader: DataLoader,
    config: dict,
    eval_steps: int | None = None,
) -> dict[str, float]:
    """Run evaluation and return a metrics dict.

    Iterates over eval_steps batches, computing AR perplexity, diffusion loss,
    System 1 token accuracy, confidence accuracy, ECE, and AUROC.

    Args:
        model: The dual-process model to evaluate.
        eval_dataloader: DataLoader yielding batches of token IDs (B, T).
        config: Full configuration dict (needs training.mask_token_id, etc.).
        eval_steps: Number of eval batches. Defaults to config value.

    Returns:
        Dict with keys: ar_perplexity, diff_loss, s1_token_accuracy,
        conf_accuracy, conf_ece, conf_auroc.
    """
    model.eval()

    train_cfg = config["training"]
    mask_token_id = train_cfg["mask_token_id"]
    min_mask_ratio = train_cfg["min_mask_ratio"]
    max_mask_ratio = train_cfg["max_mask_ratio"]

    if eval_steps is None:
        eval_steps = train_cfg.get("eval_steps", 50)

    device = next(model.parameters()).device

    total_ar_loss = 0.0
    total_diff_loss = 0.0
    total_masked_tokens = 0
    total_correct_tokens = 0
    all_confidences: list[torch.Tensor] = []
    all_correct_flags: list[torch.Tensor] = []
    num_batches = 0

    data_iter = iter(eval_dataloader)

    for _ in range(eval_steps):
        try:
            batch = next(data_iter)
        except StopIteration:
            break

        input_ids = batch.to(device)

        # --- AR perplexity ---
        ar_labels = input_ids.clone()
        ar_labels[:, :-1] = input_ids[:, 1:]
        ar_labels[:, -1] = -100
        ar_loss = model.compute_ar_loss(input_ids, ar_labels)
        total_ar_loss += ar_loss.item()

        # --- System 1 metrics ---
        masked_ids, mask_positions = create_mask(
            input_ids, mask_token_id, min_mask_ratio, max_mask_ratio,
        )
        diff_loss = model.compute_diffusion_loss(input_ids, masked_ids, mask_positions)
        total_diff_loss += diff_loss.item()

        logits, confidence, _ = model.forward_system1(masked_ids, mask_positions)

        # Token accuracy at masked positions
        predicted_ids = logits.argmax(dim=-1)
        correct = (predicted_ids == input_ids) & mask_positions
        total_correct_tokens += correct.sum().item()
        total_masked_tokens += mask_positions.sum().item()

        # Confidence metrics at masked positions
        conf_probs = torch.sigmoid(confidence)
        correct_float = (predicted_ids == input_ids).float()

        mask_flat = mask_positions.view(-1)
        conf_flat = conf_probs.view(-1)[mask_flat]
        correct_flat = correct_float.view(-1)[mask_flat]

        all_confidences.append(conf_flat.cpu())
        all_correct_flags.append(correct_flat.cpu())

        num_batches += 1

    # --- Aggregate ---
    metrics: dict[str, float] = {}

    avg_ar_loss = total_ar_loss / max(num_batches, 1)
    metrics["ar_perplexity"] = math.exp(min(avg_ar_loss, 100.0))

    metrics["diff_loss"] = total_diff_loss / max(num_batches, 1)

    metrics["s1_token_accuracy"] = total_correct_tokens / max(total_masked_tokens, 1)

    if all_confidences:
        all_conf = torch.cat(all_confidences)
        all_corr = torch.cat(all_correct_flags)

        conf_preds = (all_conf > 0.5).float()
        metrics["conf_accuracy"] = (conf_preds == all_corr).float().mean().item()

        metrics["conf_ece"] = compute_calibration_error(all_conf, all_corr)

        metrics["conf_auroc"] = compute_auroc(all_conf, all_corr)
    else:
        metrics["conf_accuracy"] = 0.0
        metrics["conf_ece"] = 0.0
        metrics["conf_auroc"] = 0.5

    model.train()
    return metrics
