# Feature Spec: Depolarizing Noise Models

**Feature ID**: 002-noise-models
**Status**: Implemented

## Overview

Build a noise model layer that wraps quantum circuit simulations with realistic depolarizing
errors. The noise model simulates how real quantum hardware degrades results: single-qubit gates
have an `error_rate` chance of a random Pauli error; two-qubit gates have 2× that rate (reflecting
real hardware physics). At `error_rate=0`, no noise model is applied (ideal simulation).

## User Stories

- As a user, I want to set error_rate=0 to simulate a perfect quantum computer.
- As a user, I want to set error_rate=0.01 to simulate IBM's best current hardware.
- As a user, I want to set error_rate=0.20 to see near-random noise effects.
- As a developer, I want a human-readable noise label for the UI (e.g. "Moderate noise").

## Requirements

1. `build_noise_model(error_rate)` returns `None` when `error_rate == 0.0`.
2. `build_noise_model(error_rate)` returns a `NoiseModel` for `error_rate > 0`.
3. Single-qubit gate error = `depolarizing_error(error_rate, 1)` applied to H, X, Z, Y, S, T.
4. Two-qubit gate error = `depolarizing_error(min(error_rate * 2, 0.99), 2)` applied to CX, CZ.
5. `describe_noise(error_rate)` returns a descriptive string label for 6 distinct ranges:
   - 0.0 → "Ideal (no noise)…"
   - ≤0.005 → "Near-ideal…"
   - ≤0.01 → "Low noise…"
   - ≤0.05 → "Moderate noise…"
   - ≤0.10 → "High noise…"
   - ≤0.15 → "Very high noise…"
   - >0.15 → "Extreme noise…"
6. Error rate is clamped to `[0, 1]` inside `build_noise_model`.

## Technical Design

- **Dependency**: `qiskit-aer.noise.NoiseModel`, `depolarizing_error`
- **Two-qubit penalty**: 2× reflects that two-qubit gates require physical qubit coupling,
  which is harder to control than single-qubit rotations.

## Acceptance Criteria

- [ ] `build_noise_model(0.0)` returns `None`
- [ ] `build_noise_model(0.05)` returns a `NoiseModel` instance
- [ ] Running Bell State at p=0.10 produces measurable |01⟩ and |10⟩ errors
- [ ] `describe_noise(0.0)` returns a string containing "Ideal"
- [ ] `describe_noise(0.05)` returns a string containing "Moderate"
- [ ] `describe_noise(0.20)` returns a string containing "Extreme"
