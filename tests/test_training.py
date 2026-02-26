"""Tests for the training loop utilities."""

import pytest
from src.training.joint_trainer import get_lr


class TestLRSchedule:
    def test_warmup_starts_at_zero(self):
        lr = get_lr(step=0, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        assert lr == 0.0

    def test_warmup_midpoint(self):
        lr = get_lr(step=50, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        assert abs(lr - 1.5e-4) < 1e-8

    def test_warmup_end_equals_max(self):
        lr = get_lr(step=100, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        assert abs(lr - 3e-4) < 1e-8

    def test_end_equals_min(self):
        lr = get_lr(step=1000, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        assert abs(lr - 3e-5) < 1e-8

    def test_cosine_decreases(self):
        lr1 = get_lr(step=200, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        lr2 = get_lr(step=500, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        lr3 = get_lr(step=900, warmup_steps=100, max_steps=1000, max_lr=3e-4, min_lr=3e-5)
        assert lr1 > lr2 > lr3
