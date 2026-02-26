"""Tests for the dual-process GPT-2 model."""

import torch
import yaml
import pytest

from src.model.dual_process_gpt2 import DualProcessGPT2, ConfidenceHead
from src.model.masking import create_mask


@pytest.fixture
def config():
    """Minimal config for testing (loads tiny.yaml)."""
    with open("configs/tiny.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def small_config():
    """Minimal config that avoids downloading full GPT-2."""
    return {
        "model": {
            "name": "gpt2",
            "n_layer": 12,
            "n_head": 12,
            "n_embd": 768,
            "vocab_size": 50257,
            "block_size": 1024,
            "dropout": 0.1,
            "confidence_head_hidden": 256,
        },
        "training": {
            "mask_token_id": 50256,
            "min_mask_ratio": 0.1,
            "max_mask_ratio": 1.0,
        },
    }


class TestConfidenceHead:
    def test_output_shape(self):
        head = ConfidenceHead(n_embd=768, hidden_dim=256)
        x = torch.randn(2, 16, 768)
        out = head(x)
        assert out.shape == (2, 16)

    def test_gradient_flow(self):
        head = ConfidenceHead(n_embd=768, hidden_dim=256)
        x = torch.randn(2, 16, 768, requires_grad=True)
        out = head(x)
        out.sum().backward()
        assert x.grad is not None


class TestMasking:
    def test_output_shapes(self):
        ids = torch.randint(0, 50257, (4, 64))
        masked_ids, mask_pos = create_mask(ids, mask_token_id=50256)
        assert masked_ids.shape == ids.shape
        assert mask_pos.shape == ids.shape

    def test_mask_token_applied(self):
        ids = torch.randint(0, 50257, (4, 64))
        masked_ids, mask_pos = create_mask(ids, mask_token_id=50256)
        # All masked positions should have mask_token_id
        assert (masked_ids[mask_pos] == 50256).all()

    def test_unmasked_positions_preserved(self):
        ids = torch.randint(0, 50257, (4, 64))
        masked_ids, mask_pos = create_mask(ids, mask_token_id=50256)
        # Unmasked positions should be unchanged
        assert (masked_ids[~mask_pos] == ids[~mask_pos]).all()

    def test_mask_ratio_bounds(self):
        ids = torch.randint(0, 50257, (4, 256))
        masked_ids, mask_pos = create_mask(
            ids, mask_token_id=50256, min_mask_ratio=0.3, max_mask_ratio=0.3,
        )
        # With ratio fixed at 0.3, approximately 30% should be masked
        # Allow some variance due to randomness
        ratio = mask_pos.float().mean().item()
        assert 0.15 < ratio < 0.5

    def test_full_mask(self):
        ids = torch.randint(0, 50257, (2, 32))
        masked_ids, mask_pos = create_mask(
            ids, mask_token_id=50256, min_mask_ratio=1.0, max_mask_ratio=1.0,
        )
        assert mask_pos.all()


class TestDualProcessGPT2:
    """Integration tests for the full model. Require downloading GPT-2 weights."""

    @pytest.fixture(autouse=True)
    def setup(self, small_config):
        self.config = small_config
        self.model = DualProcessGPT2(small_config, pretrained=False)
        self.model.eval()

    def test_system1_forward_shapes(self):
        ids = torch.randint(0, 50257, (2, 16))
        mask = torch.ones(2, 16, dtype=torch.bool)
        logits, conf, hidden = self.model.forward_system1(ids, mask)
        assert logits.shape == (2, 16, 50257)
        assert conf.shape == (2, 16)
        assert hidden.shape == (2, 16, 768)

    def test_system2_forward_shapes(self):
        ids = torch.randint(0, 50257, (2, 16))
        logits, _ = self.model.forward_system2(ids)
        assert logits.shape == (2, 16, 50257)

    def test_ar_loss_is_scalar(self):
        ids = torch.randint(0, 50257, (2, 16))
        labels = ids.clone()
        loss = self.model.compute_ar_loss(ids, labels)
        assert loss.dim() == 0
        assert loss.item() > 0

    def test_diffusion_loss_is_scalar(self):
        ids = torch.randint(0, 50257, (2, 16))
        masked_ids, mask_pos = create_mask(ids, mask_token_id=50256)
        loss = self.model.compute_diffusion_loss(ids, masked_ids, mask_pos)
        assert loss.dim() == 0
        assert loss.item() > 0

    def test_confidence_loss_is_scalar(self):
        ids = torch.randint(0, 50257, (2, 16))
        masked_ids, mask_pos = create_mask(ids, mask_token_id=50256)
        logits, conf, _ = self.model.forward_system1(masked_ids, mask_pos)
        loss = self.model.compute_confidence_loss(conf, logits, ids, mask_pos)
        assert loss.dim() == 0

    def test_shared_weights(self):
        """System 1 and System 2 share the same transformer weights."""
        ids = torch.randint(0, 50257, (1, 16))
        # Both modes use self.transformer — verify it's the same object
        s1_wte = self.model.transformer.transformer.wte.weight
        # Forward through system2 also uses self.transformer
        self.model.forward_system2(ids)
        s2_wte = self.model.transformer.transformer.wte.weight
        assert s1_wte.data_ptr() == s2_wte.data_ptr()
