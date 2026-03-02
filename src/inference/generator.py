"""Inference pipelines for dual-process generation.

System 1 (iterative unmasking): Start fully masked, progressively reveal tokens by confidence.
System 2 (autoregressive): Standard left-to-right token generation.
Hybrid: System 1 generates first; if confidence is low, escalate to System 2.
"""

import torch
import torch.nn.functional as F
from typing import Optional

from src.model.dual_process_gpt2 import DualProcessGPT2


@torch.no_grad()
def generate_system1(
    model: DualProcessGPT2,
    seq_len: int,
    mask_token_id: int,
    num_steps: int = 10,
    temperature: float = 1.0,
    device: torch.device = torch.device("cpu"),
    prompt_ids: Optional[torch.Tensor] = None,
) -> tuple[torch.Tensor, float]:
    """Generate a sequence using System 1 (iterative unmasking).

    Starts with a fully masked sequence and progressively unmasks tokens
    over `num_steps` rounds, revealing the most confident predictions first.
    Accumulates confidence scores at the moment each position is revealed,
    matching the distribution the confidence head was trained on.

    Args:
        model: Trained DualProcessGPT2 model.
        seq_len: Length of the sequence to generate.
        mask_token_id: Token ID used for masking.
        num_steps: Number of unmasking rounds.
        temperature: Sampling temperature.
        device: Device to generate on.
        prompt_ids: Optional prompt tokens (1, P) to keep unmasked as a prefix.

    Returns:
        Tuple of (generated_ids (1, seq_len), mean_confidence float).
    """
    model.eval()

    # Start fully masked
    ids = torch.full((1, seq_len), mask_token_id, dtype=torch.long, device=device)
    mask = torch.ones(1, seq_len, dtype=torch.bool, device=device)

    # If prompt provided, pin those positions as unmasked
    if prompt_ids is not None:
        P = prompt_ids.size(1)
        ids[0, :P] = prompt_ids[0, :P]
        mask[0, :P] = False

    # Accumulators for confidence at the moment each position is revealed
    accumulated_conf = torch.zeros(1, seq_len, device=device)
    conf_count = torch.zeros(1, seq_len, device=device)

    tokens_per_step = max(1, seq_len // num_steps)

    for step in range(num_steps):
        if not mask.any():
            break

        logits, confidence, _ = model.forward_system1(ids, mask)

        # Sample from predicted distribution at masked positions
        probs = F.softmax(logits / temperature, dim=-1)
        sampled = torch.multinomial(probs.view(-1, probs.size(-1)), 1).view(1, seq_len)

        # Confidence at masked positions — unmask the most confident ones
        conf_scores = torch.sigmoid(confidence)
        conf_scores[~mask] = -1.0  # already unmasked

        # Determine how many to unmask this step
        remaining = mask.sum().item()
        to_unmask = min(tokens_per_step, remaining)

        # Get indices of top-confidence masked positions
        flat_conf = conf_scores.view(-1)
        _, top_indices = flat_conf.topk(to_unmask)

        # Unmask those positions and record confidence
        for idx in top_indices:
            row = idx // seq_len
            col = idx % seq_len
            ids[row, col] = sampled[row, col]
            mask[row, col] = False
            accumulated_conf[row, col] = torch.sigmoid(confidence[row, col])
            conf_count[row, col] = 1.0

    # Fill any remaining masks (shouldn't happen, but safety)
    if mask.any():
        logits, confidence, _ = model.forward_system1(ids, mask)
        final_preds = logits.argmax(dim=-1)
        ids[mask] = final_preds[mask]
        # Record confidence for these fallback positions too
        conf_at_remaining = torch.sigmoid(confidence)
        accumulated_conf[mask] = conf_at_remaining[mask]
        conf_count[mask] = 1.0

    mean_confidence = (accumulated_conf.sum() / conf_count.sum().clamp(min=1)).item()

    return ids, mean_confidence


@torch.no_grad()
def generate_system2(
    model: DualProcessGPT2,
    prompt_ids: torch.Tensor,
    max_new_tokens: int = 128,
    temperature: float = 1.0,
    top_k: int = 50,
) -> torch.Tensor:
    """Generate tokens using System 2 (autoregressive).

    Standard left-to-right generation with top-k sampling.

    Args:
        model: Trained DualProcessGPT2 model.
        prompt_ids: Prompt token IDs of shape (1, T).
        max_new_tokens: Number of new tokens to generate.
        temperature: Sampling temperature.
        top_k: Top-k filtering parameter.

    Returns:
        Full sequence including prompt and generated tokens (1, T + new).
    """
    model.eval()
    device = prompt_ids.device
    ids = prompt_ids.clone()

    for _ in range(max_new_tokens):
        # Truncate to block_size if needed
        input_ids = ids[:, -model.block_size:]

        logits, _ = model.forward_system2(input_ids)
        next_logits = logits[:, -1, :] / temperature

        # Top-k filtering
        if top_k > 0:
            topk_vals, _ = next_logits.topk(top_k)
            threshold = topk_vals[:, -1].unsqueeze(-1)
            next_logits[next_logits < threshold] = float("-inf")

        probs = F.softmax(next_logits, dim=-1)
        next_token = torch.multinomial(probs, 1)
        ids = torch.cat([ids, next_token], dim=1)

    return ids


@torch.no_grad()
def generate_hybrid(
    model: DualProcessGPT2,
    seq_len: int,
    mask_token_id: int,
    confidence_threshold: float = 0.8,
    num_diffusion_steps: int = 10,
    max_ar_tokens: int = 128,
    temperature: float = 1.0,
    device: torch.device = torch.device("cpu"),
    prompt_ids: Optional[torch.Tensor] = None,
) -> tuple[torch.Tensor, str]:
    """Hybrid generation: System 1 first, escalate to System 2 if confidence is low.

    Confidence is accumulated during the System 1 unmasking loop (at the moment
    each position is revealed), matching the distribution the head was trained on.

    Args:
        model: Trained DualProcessGPT2 model.
        seq_len: Target sequence length for System 1.
        mask_token_id: Token ID used for masking.
        confidence_threshold: Minimum mean confidence to accept System 1 output.
        num_diffusion_steps: Iterative unmasking steps.
        max_ar_tokens: Max tokens if escalating to System 2.
        temperature: Sampling temperature.
        device: Device to generate on.
        prompt_ids: Optional prompt tokens (1, P) to keep unmasked as a prefix.

    Returns:
        Tuple of (generated_ids, system_used) where system_used is "system1" or "system2".
    """
    model.eval()

    # Try System 1 first — confidence is accumulated during unmasking
    ids, mean_conf = generate_system1(
        model, seq_len, mask_token_id, num_diffusion_steps, temperature, device,
        prompt_ids=prompt_ids,
    )

    if mean_conf >= confidence_threshold:
        return ids, "system1"

    # Escalate: use System 1 output as prompt prefix, continue with System 2
    # Take the first quarter as a prompt seed
    prompt_len = max(1, seq_len // 4)
    prompt = ids[:, :prompt_len]
    full_ids = generate_system2(model, prompt, max_new_tokens=seq_len - prompt_len, temperature=temperature)

    return full_ids, "system2"
