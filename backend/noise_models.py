"""
noise_models.py — Quantum Error and Noise Modeling
===================================================

This module creates depolarizing noise models for our quantum circuit simulations.
A noise model wraps a circuit so that every gate has a chance of failing and
introducing a random error — simulating what real quantum hardware does.

WHY NOISE MODELS MATTER:
  Real quantum computers are not perfect. Qubits interact with their environment
  (heat, electromagnetic fields, vibrations) and lose their quantum state — a
  process called decoherence. Without noise models, our simulations look too good
  to be realistic. With noise models, we can show exactly how errors degrade results.

HOW IT CONNECTS:
  quantum_engine.py calls:
    noise_model = build_noise_model(error_rate)   ← from this file
    counts = run_circuit(circuit, shots, noise_model)

  If error_rate == 0.0 → build_noise_model returns None → perfect simulation
  If error_rate  > 0.0 → returns a NoiseModel → AerSimulator applies errors

THE DEPOLARIZING CHANNEL:
  For each gate, with probability p:
    → X error (bit flip)         applied with probability p/3
    → Y error (bit+phase flip)   applied with probability p/3
    → Z error (phase flip)       applied with probability p/3
  With probability (1-p): gate works perfectly.

  This is the standard noise model used in quantum computing research papers
  and IBM's own error characterization tools.
"""

from qiskit_aer.noise import NoiseModel, depolarizing_error


def build_noise_model(error_rate: float) -> NoiseModel | None:
    """
    Build a depolarizing noise model for a given error rate.

    This is the only function quantum_engine.py needs to call.
    It creates a NoiseModel that wraps every gate with a chance of failure.

    Args:
        error_rate: float between 0.0 and 0.20
                    0.0  = perfect quantum computer (no errors)
                    0.01 = roughly IBM's best real hardware (2024)
                    0.05 = moderately noisy — errors clearly visible in chart
                    0.10 = heavily degraded — algorithms start failing
                    0.20 = very noisy — results nearly random

    Returns:
        NoiseModel  if error_rate > 0  (Aer will apply errors)
        None        if error_rate == 0 (Aer runs ideal simulation, faster)

    Example:
        noise_model = build_noise_model(0.05)
        # → Every H, X gate has 5% chance of random error
        # → Every CNOT, CZ gate has 10% chance of random error
    """
    # No noise requested — skip building a model entirely.
    # Returning None tells run_circuit() to call AerSimulator without noise_model=,
    # which runs a perfect ideal simulation (faster too).
    if error_rate <= 0.0:
        return None

    # Clamp error_rate to valid range [0, 1]
    # (user input is 0.0–0.20, but defensive programming is always good)
    error_rate = min(error_rate, 1.0)

    noise_model = NoiseModel()

    # ── Single-qubit gate error ───────────────────────────────────────────────
    # depolarizing_error(p, num_qubits):
    #   p           = probability of error (0.0 to 1.0)
    #   num_qubits  = how many qubits the gate acts on (1 here)
    #
    # This creates an error channel that, with probability p,
    # applies a random Pauli error (X, Y, or Z) to the qubit.
    single_qubit_error = depolarizing_error(error_rate, 1)

    # ── Two-qubit gate error ──────────────────────────────────────────────────
    # Two-qubit gates (CNOT, CZ) require physical coupling between qubits,
    # which is harder to control precisely. In practice, they have roughly
    # 2–10x the error rate of single-qubit gates.
    #
    # We model this with 2× the error rate, capped at 1.0.
    # min(..., 0.99) avoids edge case of fully random qubit (p=1 is unphysical)
    two_qubit_rate = min(error_rate * 2, 0.99)
    two_qubit_error = depolarizing_error(two_qubit_rate, 2)

    # ── Apply errors to specific gate types ──────────────────────────────────
    # add_all_qubit_quantum_error(error_channel, gate_names):
    #   Tells Aer: "after every gate in this list, apply this error channel
    #   to ALL qubits" — regardless of which qubit it's on.
    #
    # Single-qubit gates in our circuits: H, X, Z
    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ['h', 'x', 'z', 'y', 's', 't']  # single-qubit gate names in Qiskit
    )

    # Two-qubit gates in our circuits: CX (CNOT) and CZ
    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        ['cx', 'cz']
    )

    return noise_model


def describe_noise(error_rate: float) -> str:
    """
    Return a human-readable description of what an error rate means.

    Used by the Flask API to include a qualitative label in the response,
    so the frontend can show users contextual information about their chosen
    error rate (e.g. "Similar to current IBM quantum hardware").

    Args:
        error_rate: float 0.0 – 0.20

    Returns:
        str: descriptive label
    """
    if error_rate == 0.0:
        return "Ideal (no noise) — theoretical perfect quantum computer"
    elif error_rate <= 0.005:
        return "Near-ideal — better than current best quantum hardware"
    elif error_rate <= 0.01:
        return "Low noise — comparable to IBM's best qubits (2024)"
    elif error_rate <= 0.05:
        return "Moderate noise — errors are visible but circuit still works"
    elif error_rate <= 0.10:
        return "High noise — significant degradation, algorithms struggle"
    elif error_rate <= 0.15:
        return "Very high noise — results are mostly noise"
    else:
        return "Extreme noise — nearly random results"


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL TEST — run this file directly to see noise in action
# Command: python backend/noise_models.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys
    import os

    # Add backend/ to path so we can import quantum_engine
    sys.path.insert(0, os.path.dirname(__file__))

    from quantum_engine import build_bell_circuit, build_grover_circuit, run_circuit

    print("=" * 65)
    print("Noise Models — Manual Test")
    print("Watching Bell State degrade as error rate increases")
    print("=" * 65)

    bell = build_bell_circuit()
    SHOTS = 1024

    print(f"\n{'Rate':>6}  {'|00>':>6}  {'|01>':>6}  {'|10>':>6}  {'|11>':>6}  {'Errors':>7}  Description")
    print("-" * 85)

    for p in [0.0, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]:
        noise_model = build_noise_model(p)
        counts = run_circuit(bell, shots=SHOTS, noise_model=noise_model)

        c00 = counts.get("00", 0)
        c01 = counts.get("01", 0)
        c10 = counts.get("10", 0)
        c11 = counts.get("11", 0)
        errors = c01 + c10
        label = describe_noise(p)

        print(f"  {p:.2f}  {c00:>6}  {c01:>6}  {c10:>6}  {c11:>6}  {errors:>6}   {label}")

    print("\n" + "=" * 65)
    print("Watching Grover's Algorithm fail as noise increases")
    print("=" * 65)

    grover = build_grover_circuit()

    print(f"\n{'Rate':>6}  {'|11>':>6}  {'Others':>7}  {'Success%':>9}")
    print("-" * 40)

    for p in [0.0, 0.05, 0.10, 0.15, 0.20]:
        noise_model = build_noise_model(p)
        counts = run_circuit(grover, shots=SHOTS, noise_model=noise_model)

        c11 = counts.get("11", 0)
        others = SHOTS - c11
        pct = 100 * c11 / SHOTS

        print(f"  {p:.2f}  {c11:>6}  {others:>7}  {pct:>8.1f}%")

    print("\nNoise models working correctly!")
