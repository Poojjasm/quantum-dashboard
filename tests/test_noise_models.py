"""
tests/test_noise_models.py — Unit tests for noise model construction and labels.

Tests cover:
  - build_noise_model(0.0) returns None
  - build_noise_model(p > 0) returns a NoiseModel instance
  - describe_noise returns correct label for all 7 ranges
  - Error clamping behavior
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from noise_models import build_noise_model, describe_noise
from qiskit_aer.noise import NoiseModel


# ── build_noise_model ────────────────────────────────────────────────────────

class TestBuildNoiseModel:
    def test_zero_error_rate_returns_none(self):
        assert build_noise_model(0.0) is None

    def test_negative_error_rate_returns_none(self):
        # Negative should be treated as 0
        assert build_noise_model(-0.01) is None

    def test_positive_error_rate_returns_noise_model(self):
        model = build_noise_model(0.05)
        assert isinstance(model, NoiseModel)

    def test_small_error_rate_returns_noise_model(self):
        model = build_noise_model(0.001)
        assert isinstance(model, NoiseModel)

    def test_max_error_rate_returns_noise_model(self):
        model = build_noise_model(0.20)
        assert isinstance(model, NoiseModel)

    def test_above_max_error_rate_does_not_crash(self):
        # Should clamp to 1.0, not crash
        model = build_noise_model(1.5)
        assert isinstance(model, NoiseModel)

    def test_noise_model_has_basis_gates(self):
        model = build_noise_model(0.05)
        # NoiseModel should have errors registered on quantum error gates
        assert len(model.noise_instructions) > 0


# ── describe_noise labels ────────────────────────────────────────────────────

class TestDescribeNoise:
    def test_zero_is_ideal(self):
        label = describe_noise(0.0)
        assert 'Ideal' in label or 'ideal' in label

    def test_very_small_is_near_ideal(self):
        label = describe_noise(0.003)
        assert 'Near' in label or 'near' in label

    def test_low_noise(self):
        label = describe_noise(0.01)
        assert 'Low' in label or 'low' in label

    def test_moderate_noise(self):
        label = describe_noise(0.05)
        assert 'Moderate' in label or 'moderate' in label

    def test_high_noise(self):
        label = describe_noise(0.10)
        assert 'High' in label or 'high' in label

    def test_very_high_noise(self):
        label = describe_noise(0.15)
        assert 'high' in label.lower()

    def test_extreme_noise(self):
        label = describe_noise(0.20)
        assert 'Extreme' in label or 'extreme' in label

    def test_all_labels_are_non_empty_strings(self):
        for rate in [0.0, 0.005, 0.01, 0.05, 0.10, 0.15, 0.20]:
            label = describe_noise(rate)
            assert isinstance(label, str)
            assert len(label) > 0

    def test_labels_contain_dash_separator(self):
        # All labels use " — " to separate the short name from the description
        for rate in [0.0, 0.01, 0.05, 0.10, 0.20]:
            label = describe_noise(rate)
            assert '—' in label, f"Label for {rate} missing ' — ' separator: {label}"
