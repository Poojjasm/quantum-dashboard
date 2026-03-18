# Feature Spec: Quantum Circuit Engine

**Feature ID**: 001-quantum-engine
**Status**: Implemented

## Overview

Build a quantum circuit simulation engine that runs four canonical quantum circuits (Bell State,
GHZ State, Quantum Teleportation, Grover's Algorithm) on a classical CPU using IBM's Qiskit and
Qiskit Aer simulator. The engine accepts a circuit name, error rate, and shot count, and returns
a measurement count dictionary suitable for JSON serialization.

## User Stories

- As a user, I want to simulate a Bell State circuit so I can see quantum entanglement in action.
- As a user, I want to simulate a GHZ circuit with 3 qubits to observe multi-qubit entanglement.
- As a user, I want to simulate Quantum Teleportation to see how quantum state transfer works.
- As a user, I want to simulate Grover's Algorithm to see quantum speedup over classical search.
- As a user, I want to see ideal (noiseless) reference distributions for each circuit.

## Requirements

1. Implement `build_bell_circuit()` — 2-qubit entangled state producing only |00⟩ and |11⟩ ideally.
2. Implement `build_ghz_circuit()` — 3-qubit entangled state producing only |000⟩ and |111⟩ ideally.
3. Implement `build_teleportation_circuit()` — 3-qubit teleportation where Bob's qubit matches Alice's.
4. Implement `build_grover_circuit()` — 2-qubit Grover search that amplifies |11⟩ to ~100%.
5. Implement `run_named_circuit(name, error_rate, shots)` — dispatcher calling the correct builder.
6. Implement `get_ideal_counts(name, shots)` — returns theoretical distribution × shots.
7. `CIRCUIT_BUILDERS` dict maps string names to builder functions (single source of truth).
8. Return plain Python `dict` (not Qiskit Counter) for JSON serialization compatibility.

## Technical Design

- **Language**: Python 3.11+
- **Dependencies**: `qiskit>=2.0`, `qiskit-aer>=0.15`
- **Key classes**: `QuantumCircuit`, `AerSimulator`, `transpile`
- **Pattern**: Builder functions return `QuantumCircuit`; `run_circuit()` executes via AerSimulator.
- **Ideal distributions**: Stored in `IDEAL_DISTRIBUTIONS` dict as probability fractions.

## Acceptance Criteria

- [ ] Bell State: ideal run produces only `00` and `11` keys in counts dict
- [ ] GHZ State: ideal run produces only `000` and `111` keys
- [ ] Grover: ideal run produces `11` with ~100% probability
- [ ] Teleportation: leftmost bit (q2) is always `1` in ideal run
- [ ] `run_named_circuit` raises `ValueError` for unknown circuit names
- [ ] `get_ideal_counts` returns counts summing to exactly `shots`
- [ ] All 4 circuits accessible via `CIRCUIT_BUILDERS` dict
