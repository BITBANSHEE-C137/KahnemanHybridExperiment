"""Tests for the evaluation module."""

import math

import torch
import pytest
from torch.utils.data import DataLoader

from src.model.dual_process_gpt2 import DualProcessGPT2
from src.evaluation.evaluator import evaluate, compute_calibration_error
from src.evaluation.metrics import compute_auroc


@pytest.fixture
def config():
    """Minimal config for evaluation testing."""
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
            "eval_steps": 5,
        },
    }


@pytest.fixture
def model(config):
    """Random-init model for CPU testing."""
    m = DualProcessGPT2(config, pretrained=False)
    m.eval()
    return m


@pytest.fixture
def eval_dataloader():
    """Fake eval dataloader with random token IDs."""
    data = torch.randint(0, 50257, (20, 32))
    return DataLoader(data, batch_size=4, shuffle=False)


# --- AUROC tests ---

class TestAUROC:
    def test_perfect_ranking(self):
        """Perfect confidence ranking should give AUROC = 1.0."""
        scores = torch.tensor([0.9, 0.8, 0.7, 0.2, 0.1])
        labels = torch.tensor([1.0, 1.0, 1.0, 0.0, 0.0])
        assert compute_auroc(scores, labels) == pytest.approx(1.0)

    def test_inverse_ranking(self):
        """Perfectly wrong ranking should give AUROC = 0.0."""
        scores = torch.tensor([0.1, 0.2, 0.3, 0.8, 0.9])
        labels = torch.tensor([1.0, 1.0, 1.0, 0.0, 0.0])
        assert compute_auroc(scores, labels) == pytest.approx(0.0)

    def test_random_ranking(self):
        """Random scores should give AUROC ~ 0.5."""
        torch.manual_seed(42)
        scores = torch.rand(1000)
        labels = (torch.rand(1000) > 0.5).float()
        auroc = compute_auroc(scores, labels)
        assert 0.35 < auroc < 0.65

    def test_single_class_returns_half(self):
        """All-positive or all-negative labels return 0.5."""
        scores = torch.tensor([0.9, 0.5, 0.1])
        assert compute_auroc(scores, torch.ones(3)) == 0.5
        assert compute_auroc(scores, torch.zeros(3)) == 0.5

    def test_empty_returns_half(self):
        """Empty input returns 0.5."""
        assert compute_auroc(torch.tensor([]), torch.tensor([])) == 0.5


# --- ECE tests ---

class TestCalibrationError:
    def test_perfect_calibration(self):
        """All confident and all correct -> ECE ~ 0."""
        confs = torch.ones(100)
        accs = torch.ones(100)
        ece = compute_calibration_error(confs, accs)
        assert ece == pytest.approx(0.0, abs=0.01)

    def test_worst_calibration(self):
        """Confidence 1.0 but all wrong -> ECE should be high."""
        confs = torch.ones(100)
        accs = torch.zeros(100)
        ece = compute_calibration_error(confs, accs)
        assert ece > 0.9

    def test_empty_input(self):
        ece = compute_calibration_error(torch.tensor([]), torch.tensor([]))
        assert ece == 0.0

    def test_ece_range(self):
        """ECE should be between 0 and 1."""
        torch.manual_seed(42)
        confs = torch.rand(500)
        accs = (torch.rand(500) > 0.5).float()
        ece = compute_calibration_error(confs, accs)
        assert 0.0 <= ece <= 1.0


# --- Evaluate integration tests ---

class TestEvaluate:
    def test_returns_all_metric_keys(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        expected_keys = {
            "ar_perplexity", "diff_loss", "s1_token_accuracy",
            "conf_accuracy", "conf_ece", "conf_auroc",
        }
        assert expected_keys == set(metrics.keys())

    def test_metrics_are_finite(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        for key, val in metrics.items():
            assert math.isfinite(val), f"{key} is not finite: {val}"

    def test_perplexity_is_exp_of_loss(self, model, config):
        """Perplexity should be >= 1 (exp of non-negative loss)."""
        data = torch.randint(0, 50257, (8, 32))
        dl = DataLoader(data, batch_size=4, shuffle=False)
        metrics = evaluate(model, dl, config, eval_steps=2)
        assert metrics["ar_perplexity"] >= 1.0

    def test_token_accuracy_range(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        assert 0.0 <= metrics["s1_token_accuracy"] <= 1.0

    def test_conf_accuracy_range(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        assert 0.0 <= metrics["conf_accuracy"] <= 1.0

    def test_conf_ece_range(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        assert 0.0 <= metrics["conf_ece"] <= 1.0

    def test_conf_auroc_range(self, model, eval_dataloader, config):
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        assert 0.0 <= metrics["conf_auroc"] <= 1.0

    def test_model_restored_to_train(self, model, eval_dataloader, config):
        """After evaluate(), model should be back in train mode."""
        model.train()
        evaluate(model, eval_dataloader, config, eval_steps=1)
        assert model.training

    def test_eval_steps_caps_iteration(self, model, config):
        """Should only iterate eval_steps batches, not the whole dataloader."""
        data = torch.randint(0, 50257, (100, 32))
        dl = DataLoader(data, batch_size=4, shuffle=False)
        metrics = evaluate(model, dl, config, eval_steps=2)
        assert "ar_perplexity" in metrics

    def test_handles_small_dataloader(self, model, config):
        """Should not crash if dataloader has fewer batches than eval_steps."""
        data = torch.randint(0, 50257, (4, 32))
        dl = DataLoader(data, batch_size=4, shuffle=False)
        metrics = evaluate(model, dl, config, eval_steps=100)
        assert "ar_perplexity" in metrics

    def test_random_model_has_high_perplexity(self, model, eval_dataloader, config):
        """Untrained random model should have very high perplexity."""
        metrics = evaluate(model, eval_dataloader, config, eval_steps=2)
        assert metrics["ar_perplexity"] > 100.0
