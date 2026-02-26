"""Tests for inference / generation pipelines."""

import torch
import yaml
import pytest

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.inference.generator import generate_system1, generate_system2, generate_hybrid


@pytest.fixture
def model():
    config = {
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
    }
    m = DualProcessGPT2(config, pretrained=False)
    m.eval()
    return m


class TestSystem1Generation:
    def test_output_shape(self, model):
        ids = generate_system1(
            model, seq_len=16, mask_token_id=50256, num_steps=3,
        )
        assert ids.shape == (1, 16)

    def test_no_mask_tokens_remain(self, model):
        ids = generate_system1(
            model, seq_len=16, mask_token_id=50256, num_steps=5,
        )
        assert (ids != 50256).all()


class TestSystem2Generation:
    def test_output_length(self, model):
        prompt = torch.randint(0, 50257, (1, 8))
        ids = generate_system2(model, prompt, max_new_tokens=16)
        assert ids.shape == (1, 24)  # 8 prompt + 16 new


class TestHybridGeneration:
    def test_returns_valid_output(self, model):
        ids, system_used = generate_hybrid(
            model, seq_len=16, mask_token_id=50256,
            confidence_threshold=0.0,  # always accept System 1
            num_diffusion_steps=3,
        )
        assert ids.shape[0] == 1
        assert system_used in ("system1", "system2")

    def test_low_threshold_uses_system1(self, model):
        _, system_used = generate_hybrid(
            model, seq_len=16, mask_token_id=50256,
            confidence_threshold=0.0,  # always accept
            num_diffusion_steps=3,
        )
        assert system_used == "system1"
