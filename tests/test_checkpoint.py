"""Tests for checkpoint save/load round-trip integrity."""

import torch
import pytest

from src.model.dual_process_gpt2 import DualProcessGPT2


@pytest.fixture
def config():
    """Minimal config for checkpoint tests."""
    return {
        "model": {
            "name": "gpt2",
            "n_layer": 12,
            "n_head": 12,
            "n_embd": 768,
            "vocab_size": 50257,
            "block_size": 1024,
            "dropout": 0.0,
            "confidence_head_hidden": 256,
        },
        "training": {
            "mask_token_id": 50256,
        },
    }


class TestCheckpointRoundTrip:
    def test_checkpoint_weights_match(self, config, tmp_path):
        """Save model state_dict, load into fresh model, assert all weights match."""
        torch.manual_seed(42)
        model_a = DualProcessGPT2(config, pretrained=False)

        ckpt_path = tmp_path / "weights.pt"
        torch.save(model_a.state_dict(), ckpt_path)

        torch.manual_seed(99)  # different seed so fresh model has different init
        model_b = DualProcessGPT2(config, pretrained=False)
        model_b.load_state_dict(torch.load(ckpt_path, weights_only=True))

        for name, param_a in model_a.named_parameters():
            param_b = dict(model_b.named_parameters())[name]
            assert torch.equal(param_a, param_b), f"Mismatch in parameter: {name}"

    def test_checkpoint_optimizer_state(self, config, tmp_path):
        """Save model+optimizer state after one step, load into fresh pair, assert match."""
        torch.manual_seed(42)
        model_a = DualProcessGPT2(config, pretrained=False)
        optimizer_a = torch.optim.AdamW(model_a.parameters(), lr=1e-4)

        # One forward + backward pass to populate optimizer state
        ids = torch.randint(0, 50257, (2, 16))
        loss = model_a.compute_ar_loss(ids, ids.clone())
        loss.backward()
        optimizer_a.step()

        ckpt_path = tmp_path / "optim.pt"
        torch.save({
            "model": model_a.state_dict(),
            "optimizer": optimizer_a.state_dict(),
        }, ckpt_path)

        # Load into fresh model + optimizer
        torch.manual_seed(99)
        model_b = DualProcessGPT2(config, pretrained=False)
        optimizer_b = torch.optim.AdamW(model_b.parameters(), lr=1e-4)

        ckpt = torch.load(ckpt_path, weights_only=True)
        model_b.load_state_dict(ckpt["model"])
        optimizer_b.load_state_dict(ckpt["optimizer"])

        # Compare optimizer state dicts
        state_a = optimizer_a.state_dict()
        state_b = optimizer_b.state_dict()

        assert state_a["param_groups"] == state_b["param_groups"]
        for key in state_a["state"]:
            for k, v in state_a["state"][key].items():
                if isinstance(v, torch.Tensor):
                    assert torch.equal(v, state_b["state"][key][k]), \
                        f"Optimizer state mismatch: param {key}, key {k}"
                else:
                    assert v == state_b["state"][key][k]

    def test_checkpoint_forward_output(self, config, tmp_path):
        """Save checkpoint, load into fresh model, assert identical forward outputs."""
        torch.manual_seed(42)
        model_a = DualProcessGPT2(config, pretrained=False)
        model_a.eval()

        ckpt_path = tmp_path / "forward.pt"
        torch.save(model_a.state_dict(), ckpt_path)

        torch.manual_seed(99)
        model_b = DualProcessGPT2(config, pretrained=False)
        model_b.load_state_dict(torch.load(ckpt_path, weights_only=True))
        model_b.eval()

        ids = torch.randint(0, 50257, (2, 16))
        with torch.no_grad():
            logits_a, _ = model_a.forward_system2(ids)
            logits_b, _ = model_b.forward_system2(ids)

        assert torch.equal(logits_a, logits_b), \
            f"Forward output mismatch. Max diff: {(logits_a - logits_b).abs().max().item()}"
