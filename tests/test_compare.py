"""Tests for scripts/compare_systems.py — runs on random-init model."""

import torch
import yaml
import pytest

from src.model.dual_process_gpt2 import DualProcessGPT2
from transformers import GPT2Tokenizer


@pytest.fixture
def config():
    with open("configs/tiny.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def model(config):
    model = DualProcessGPT2(config, pretrained=False)
    model.eval()
    return model


@pytest.fixture
def tokenizer():
    return GPT2Tokenizer.from_pretrained("gpt2")


class TestEscalationAnalysis:
    def test_returns_all_thresholds(self, model, tokenizer, config):
        from scripts.compare_systems import analyze_escalation
        thresholds = [0.5, 0.8]
        results = analyze_escalation(model, tokenizer, config, thresholds=thresholds, num_examples=5)
        for t in thresholds:
            assert t in results
            assert 0 <= results[t] <= 100

    def test_higher_threshold_more_escalation(self, model, tokenizer, config):
        from scripts.compare_systems import analyze_escalation
        results = analyze_escalation(model, tokenizer, config, thresholds=[0.1, 0.99], num_examples=10)
        # With threshold 0.99, more tokens should be escalated than 0.1
        assert results[0.99] >= results[0.1]


class TestSpeedComparison:
    def test_returns_all_modes(self, model, config):
        from scripts.compare_systems import compare_speed
        results = compare_speed(model, config, seq_len=16, num_trials=2, warmup=1)
        assert len(results) == 3
        for mode, (mean, std) in results.items():
            assert mean > 0
            assert std >= 0


class TestQualityComparison:
    def test_returns_all_modes(self, model, config):
        from scripts.compare_systems import compare_quality
        results = compare_quality(model, config, num_samples=2, seq_len=16)
        assert "System 1" in results
        assert "System 2" in results
        assert "Hybrid" in results
        for mode, ppl in results.items():
            assert ppl > 0


class TestConfidenceAnalysis:
    def test_returns_metrics(self, model, config):
        from scripts.compare_systems import analyze_confidence
        results = analyze_confidence(model, config, num_examples=5)
        assert "ece" in results
        assert "auroc" in results
        assert "mean_confidence" in results
        assert 0 <= results["ece"] <= 1
        assert 0 <= results["mean_confidence"] <= 1


class TestPrintResults:
    def test_print_does_not_crash(self, capsys):
        from scripts.compare_systems import print_results
        escalation = {0.5: 30.0, 0.8: 65.0}
        speed = {
            "System 1 (diffusion)": (150.0, 10.0),
            "System 2 (AR)": (80.0, 5.0),
            "Hybrid (thresh=0.8)": (120.0, 8.0),
        }
        quality = {"System 1": 45.0, "System 2": 30.0, "Hybrid": 35.0}
        confidence = {"ece": 0.123, "auroc": 0.750, "mean_confidence": 0.650}
        print_results(escalation, speed, quality, confidence, "5000")
        captured = capsys.readouterr()
        assert "SYSTEM 1 vs SYSTEM 2" in captured.out
        assert "ESCALATION" in captured.out
