"""Evaluation metrics for the dual-process model.

Provides AUROC computation without requiring sklearn.
"""

import torch


def compute_auroc(scores: torch.Tensor, labels: torch.Tensor) -> float:
    """Compute Area Under the ROC Curve.

    Uses the trapezoidal rule on the ROC curve constructed by sorting
    predictions. No external dependencies required.

    Args:
        scores: Predicted confidence scores, shape (N,). Higher = more confident.
        labels: Binary ground-truth labels, shape (N,). 1 = positive, 0 = negative.

    Returns:
        AUROC value between 0.0 and 1.0. Returns 0.5 if only one class present.
    """
    if scores.numel() == 0:
        return 0.5

    labels = labels.float()
    num_pos = labels.sum().item()
    num_neg = labels.numel() - num_pos

    # Need both classes for a meaningful AUROC
    if num_pos == 0 or num_neg == 0:
        return 0.5

    # Sort by descending score
    sorted_indices = scores.argsort(descending=True)
    sorted_labels = labels[sorted_indices]

    # Walk through sorted predictions, tracking TPR and FPR
    tp = 0.0
    fp = 0.0
    prev_fpr = 0.0
    prev_tpr = 0.0
    auc = 0.0

    for label in sorted_labels:
        if label == 1.0:
            tp += 1.0
        else:
            fp += 1.0

        tpr = tp / num_pos
        fpr = fp / num_neg

        # Trapezoidal area
        auc += (fpr - prev_fpr) * (tpr + prev_tpr) / 2.0
        prev_fpr = fpr
        prev_tpr = tpr

    return auc
