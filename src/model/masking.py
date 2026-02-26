"""Masking utilities for the diffusion (System 1) forward process.

Implements the masked diffusion strategy from LLaDA: at each training step,
sample a masking ratio t ~ U(min_ratio, max_ratio) and randomly mask that
fraction of tokens.
"""

import torch


def create_mask(
    input_ids: torch.Tensor,
    mask_token_id: int,
    min_mask_ratio: float = 0.1,
    max_mask_ratio: float = 1.0,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Apply random masking to a batch of token sequences.

    Samples a masking ratio uniformly, then masks that fraction of tokens
    per sequence independently.

    Args:
        input_ids: Original token IDs of shape (B, T).
        mask_token_id: Token ID to use as the mask token.
        min_mask_ratio: Minimum fraction of tokens to mask.
        max_mask_ratio: Maximum fraction of tokens to mask.

    Returns:
        Tuple of:
            - masked_ids: Token IDs with masks applied (B, T).
            - mask_positions: Boolean tensor of masked positions (B, T).
    """
    batch_size, seq_len = input_ids.shape
    device = input_ids.device

    # Sample a single masking ratio for the whole batch
    t = torch.empty(1, device=device).uniform_(min_mask_ratio, max_mask_ratio).item()

    # Create random mask per token
    rand = torch.rand(batch_size, seq_len, device=device)
    mask_positions = rand < t

    # Apply mask
    masked_ids = input_ids.clone()
    masked_ids[mask_positions] = mask_token_id

    return masked_ids, mask_positions
