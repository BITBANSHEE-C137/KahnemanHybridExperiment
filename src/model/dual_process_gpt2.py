"""Dual-process GPT-2: shared-weight Transformer with System 1 (diffusion) and System 2 (AR) modes.

The key insight: the same GPT-2 weights work for both masked diffusion and
autoregressive generation. The only difference is the attention mask:
  - System 1 (diffusion): bidirectional attention, predict masked tokens
  - System 2 (autoregressive): causal attention, next-token prediction

A confidence head on top of the diffusion output decides whether to escalate.
"""

import torch
import torch.nn as nn
from transformers import GPT2LMHeadModel, GPT2Config


class ConfidenceHead(nn.Module):
    """MLP that predicts per-token confidence from hidden states.

    Args:
        n_embd: Hidden dimension of the transformer.
        hidden_dim: Intermediate dimension of the confidence MLP.
    """

    def __init__(self, n_embd: int, hidden_dim: int) -> None:
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_embd, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, hidden_states: torch.Tensor) -> torch.Tensor:
        """Predict per-token confidence scores.

        Args:
            hidden_states: Transformer hidden states of shape (B, T, D).

        Returns:
            Confidence logits of shape (B, T).
        """
        return self.net(hidden_states).squeeze(-1)


class DualProcessGPT2(nn.Module):
    """Dual-process language model wrapping GPT-2.

    Supports two modes via the same weights:
      - System 1 (diffusion): bidirectional attention for masked token prediction
      - System 2 (autoregressive): causal attention for next-token prediction

    Args:
        config: Dictionary of model configuration (from YAML).
    """

    def __init__(self, config: dict, pretrained: bool = True) -> None:
        super().__init__()
        model_cfg = config["model"]
        self.vocab_size = model_cfg["vocab_size"]
        self.block_size = model_cfg["block_size"]
        self.n_embd = model_cfg["n_embd"]

        # Load GPT-2: pretrained weights or random init
        if pretrained:
            # Pre-set loss_type to suppress transformers 5.x warning during loading
            override = GPT2Config.from_pretrained(model_cfg["name"])
            override.loss_type = "ForCausalLMLoss"
            self.transformer = GPT2LMHeadModel.from_pretrained(
                model_cfg["name"], config=override
            )
        else:
            gpt2_config = GPT2Config(
                vocab_size=self.vocab_size,
                n_positions=self.block_size,
                n_embd=self.n_embd,
                n_layer=model_cfg["n_layer"],
                n_head=model_cfg["n_head"],
                resid_pdrop=model_cfg.get("dropout", 0.1),
                embd_pdrop=model_cfg.get("dropout", 0.1),
                attn_pdrop=model_cfg.get("dropout", 0.1),
                loss_type="ForCausalLMLoss",
            )
            self.transformer = GPT2LMHeadModel(gpt2_config)

        # Confidence head for System 1 escalation decisions
        self.confidence_head = ConfidenceHead(
            n_embd=self.n_embd,
            hidden_dim=model_cfg.get("confidence_head_hidden", 256),
        )

    def _make_bidirectional_mask(self, seq_len: int, device: torch.device) -> torch.Tensor:
        """Create a bidirectional (all-ones) attention mask.

        Args:
            seq_len: Sequence length.
            device: Target device.

        Returns:
            Attention mask of shape (1, 1, T, T) with all ones.
        """
        return torch.ones(1, 1, seq_len, seq_len, device=device)

    def _forward_transformer(
        self,
        input_ids: torch.Tensor,
        attention_mask_2d: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """Run GPT-2 forward pass with a custom attention mask.

        Args:
            input_ids: Token IDs of shape (B, T).
            attention_mask_2d: 4D attention mask of shape (1, 1, T, T).

        Returns:
            Tuple of (logits (B, T, V), hidden_states (B, T, D)).
        """
        transformer_model = self.transformer.transformer
        lm_head = self.transformer.lm_head

        # Get embeddings
        inputs_embeds = transformer_model.wte(input_ids)
        position_ids = torch.arange(input_ids.size(1), device=input_ids.device).unsqueeze(0)
        position_embeds = transformer_model.wpe(position_ids)
        hidden = transformer_model.drop(inputs_embeds + position_embeds)

        # Convert attention_mask_2d to the format HF expects:
        # 0 for attend, large negative for mask
        # Our mask: 1=attend, 0=mask. Convert: (1 - mask) * -10000
        causal_mask = (1.0 - attention_mask_2d) * torch.finfo(hidden.dtype).min

        for block in transformer_model.h:
            hidden = block(hidden, attention_mask=causal_mask)[0]

        hidden = transformer_model.ln_f(hidden)
        logits = lm_head(hidden)

        return logits, hidden

    def forward_system1(
        self,
        input_ids: torch.Tensor,
        mask_positions: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        """System 1 forward pass: bidirectional diffusion.

        Args:
            input_ids: Token IDs with some positions masked, shape (B, T).
            mask_positions: Boolean tensor marking masked positions, shape (B, T).

        Returns:
            Tuple of:
                - logits: Predictions over vocab at all positions (B, T, V)
                - confidence: Per-token confidence logits (B, T)
                - hidden_states: Transformer hidden states (B, T, D)
        """
        seq_len = input_ids.size(1)
        attn_mask = self._make_bidirectional_mask(seq_len, input_ids.device)

        logits, hidden = self._forward_transformer(input_ids, attn_mask)
        confidence = self.confidence_head(hidden)

        return logits, confidence, hidden

    def forward_system2(
        self,
        input_ids: torch.Tensor,
    ) -> tuple[torch.Tensor, torch.Tensor]:
        """System 2 forward pass: causal autoregressive.

        Args:
            input_ids: Token IDs of shape (B, T).

        Returns:
            Tuple of:
                - logits: Next-token predictions (B, T, V)
                - hidden_states: None (not needed for AR mode)
        """
        outputs = self.transformer(input_ids, output_hidden_states=False)
        return outputs.logits, None

    def compute_ar_loss(
        self,
        input_ids: torch.Tensor,
        labels: torch.Tensor,
    ) -> torch.Tensor:
        """Compute autoregressive (System 2) cross-entropy loss.

        Args:
            input_ids: Input token IDs (B, T).
            labels: Target token IDs (B, T). Typically input_ids shifted by 1.

        Returns:
            Scalar AR loss.
        """
        outputs = self.transformer(input_ids, labels=labels)
        return outputs.loss

    def compute_diffusion_loss(
        self,
        input_ids: torch.Tensor,
        masked_ids: torch.Tensor,
        mask_positions: torch.Tensor,
    ) -> torch.Tensor:
        """Compute masked diffusion (System 1) cross-entropy loss.

        Only computes loss on masked positions, following LLaDA.

        Args:
            input_ids: Original (unmasked) token IDs (B, T).
            masked_ids: Token IDs with masks applied (B, T).
            mask_positions: Boolean tensor of masked positions (B, T).

        Returns:
            Scalar diffusion loss (averaged over masked tokens).
        """
        logits, _, _ = self.forward_system1(masked_ids, mask_positions)

        # Only compute loss on masked positions
        loss_fn = nn.CrossEntropyLoss(reduction="none")
        # logits: (B, T, V), input_ids: (B, T)
        per_token_loss = loss_fn(
            logits.view(-1, self.vocab_size),
            input_ids.view(-1),
        ).view(input_ids.shape)

        # Mask out non-masked positions
        masked_loss = per_token_loss * mask_positions.float()

        # Average over masked tokens only
        num_masked = mask_positions.float().sum()
        if num_masked > 0:
            return masked_loss.sum() / num_masked
        return masked_loss.sum()

    def compute_confidence_loss(
        self,
        confidence_logits: torch.Tensor,
        predicted_logits: torch.Tensor,
        true_ids: torch.Tensor,
        mask_positions: torch.Tensor,
    ) -> torch.Tensor:
        """Compute confidence head loss.

        The confidence head should predict 1 where System 1 got the right answer,
        and 0 where it didn't. Only scored on masked positions.

        Args:
            confidence_logits: Raw confidence predictions (B, T).
            predicted_logits: System 1 vocab logits (B, T, V).
            true_ids: Ground-truth token IDs (B, T).
            mask_positions: Boolean tensor of masked positions (B, T).

        Returns:
            Scalar confidence loss (BCE, averaged over masked tokens).
        """
        # Target: did System 1 predict the correct token?
        predicted_ids = predicted_logits.argmax(dim=-1)  # (B, T)
        correct = (predicted_ids == true_ids).float()  # (B, T)

        loss_fn = nn.BCEWithLogitsLoss(reduction="none")
        per_token_loss = loss_fn(confidence_logits, correct)

        # Only on masked positions
        masked_loss = per_token_loss * mask_positions.float()
        num_masked = mask_positions.float().sum()
        if num_masked > 0:
            return masked_loss.sum() / num_masked
        return masked_loss.sum()
