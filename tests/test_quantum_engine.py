"""
tests/test_quantum_engine.py — Unit tests for the quantum circuit engine.

Tests cover:
  - CIRCUIT_BUILDERS registry has all 4 circuits
  - get_ideal_counts returns correct shapes and totals
  - run_named_circuit raises ValueError for unknown circuit names
  - Bell State ideal run produces only |00> and |11>
  - Grover ideal run produces |11> with high probability
  - run_named_circuit returns a plain dict (JSON-serializable)
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from quantum_engine import (
    CIRCUIT_BUILDERS,
    IDEAL_DISTRIBUTIONS,
    get_ideal_counts,
    run_named_circuit,
    build_bell_circuit,
    build_ghz_circuit,
    build_grover_circuit,
    build_teleportation_circuit,
)


# ── CIRCUIT_BUILDERS registry ────────────────────────────────────────────────

class TestCircuitBuilders:
    def test_has_four_circuits(self):
        assert len(CIRCUIT_BUILDERS) == 4

    def test_contains_bell(self):
        assert 'bell' in CIRCUIT_BUILDERS

    def test_contains_ghz(self):
        assert 'ghz' in CIRCUIT_BUILDERS

    def test_contains_teleportation(self):
        assert 'teleportation' in CIRCUIT_BUILDERS

    def test_contains_grover(self):
        assert 'grover' in CIRCUIT_BUILDERS

    def test_all_values_are_callable(self):
        for name, builder in CIRCUIT_BUILDERS.items():
            assert callable(builder), f"{name} builder is not callable"


# ── get_ideal_counts ─────────────────────────────────────────────────────────

class TestGetIdealCounts:
    def test_bell_sums_to_shots(self):
        ideal = get_ideal_counts('bell', 1024)
        assert sum(ideal.values()) == 1024

    def test_bell_has_only_00_and_11(self):
        ideal = get_ideal_counts('bell', 1024)
        assert set(ideal.keys()) == {'00', '11'}

    def test_ghz_has_only_000_and_111(self):
        ideal = get_ideal_counts('ghz', 512)
        assert set(ideal.keys()) == {'000', '111'}

    def test_grover_has_only_11(self):
        ideal = get_ideal_counts('grover', 1024)
        assert set(ideal.keys()) == {'11'}
        assert ideal['11'] == 1024

    def test_teleportation_has_four_states(self):
        ideal = get_ideal_counts('teleportation', 1024)
        assert len(ideal) == 4

    def test_teleportation_all_states_start_with_1(self):
        # q2 (leftmost bit in Qiskit output) should be 1 — teleportation succeeded
        ideal = get_ideal_counts('teleportation', 1024)
        for state in ideal:
            assert state[0] == '1', f"State {state} should have q2=1"

    def test_unknown_circuit_returns_empty(self):
        result = get_ideal_counts('nonexistent', 1024)
        assert result == {}

    def test_respects_shot_count(self):
        ideal_512 = get_ideal_counts('bell', 512)
        ideal_1024 = get_ideal_counts('bell', 1024)
        assert sum(ideal_512.values()) == 512
        assert sum(ideal_1024.values()) == 1024


# ── run_named_circuit validation ─────────────────────────────────────────────

class TestRunNamedCircuitValidation:
    def test_raises_value_error_for_unknown_circuit(self):
        with pytest.raises(ValueError, match="Unknown circuit"):
            run_named_circuit('fake_circuit', 0.0, 100)

    def test_raises_for_empty_string(self):
        with pytest.raises(ValueError):
            run_named_circuit('', 0.0, 100)


# ── run_named_circuit simulation (ideal, small shots) ────────────────────────

class TestRunNamedCircuitIdeal:
    """Run circuits at error_rate=0 with small shot counts for speed."""

    def test_bell_returns_dict(self):
        counts = run_named_circuit('bell', 0.0, 100)
        assert isinstance(counts, dict)

    def test_bell_total_equals_shots(self):
        shots = 200
        counts = run_named_circuit('bell', 0.0, shots)
        assert sum(counts.values()) == shots

    def test_bell_ideal_only_00_and_11(self):
        counts = run_named_circuit('bell', 0.0, 512)
        assert set(counts.keys()).issubset({'00', '11'})

    def test_ghz_ideal_only_000_and_111(self):
        counts = run_named_circuit('ghz', 0.0, 512)
        assert set(counts.keys()).issubset({'000', '111'})

    def test_grover_ideal_mostly_11(self):
        counts = run_named_circuit('grover', 0.0, 512)
        # Grover's should find |11> with very high probability (>90%) at error_rate=0
        assert counts.get('11', 0) > 450

    def test_returns_plain_dict_not_counter(self):
        counts = run_named_circuit('bell', 0.0, 100)
        assert type(counts) is dict  # must be plain dict, not Counter subclass

    def test_all_counts_are_positive_integers(self):
        counts = run_named_circuit('bell', 0.0, 100)
        for state, count in counts.items():
            assert isinstance(count, int)
            assert count > 0


# ── run_named_circuit with noise ─────────────────────────────────────────────

class TestRunNamedCircuitWithNoise:
    def test_noisy_bell_still_sums_to_shots(self):
        shots = 200
        counts = run_named_circuit('bell', 0.10, shots)
        assert sum(counts.values()) == shots

    def test_noisy_bell_introduces_error_states(self):
        # At p=0.15, errors states |01> and |10> should appear
        counts = run_named_circuit('bell', 0.15, 512)
        error_count = counts.get('01', 0) + counts.get('10', 0)
        assert error_count > 0, "High noise should produce error states"
