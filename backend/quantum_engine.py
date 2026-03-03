"""
quantum_engine.py — Quantum Circuit Simulator
==============================================

This module builds and runs the 4 quantum circuits at the heart of this project.
It uses IBM's Qiskit library to define circuits and Qiskit Aer to simulate them
on a classical CPU.

ARCHITECTURE:
  Flask API (app.py)
       ↓ calls run_named_circuit(name, error_rate, shots)
  quantum_engine.py          ← YOU ARE HERE
       ↓ uses
  noise_models.py            (we'll build this next)
       ↓ results flow back up to Flask → database → browser

KEY CONCEPTS (read QUANTUM_CONCEPTS.md for full explanations):
  - Qubit: quantum bit, can be in superposition (0 and 1 simultaneously)
  - H gate: Hadamard — creates 50/50 superposition from a definite state
  - X gate: Pauli-X — quantum NOT gate, flips |0⟩↔|1⟩
  - CNOT/CX gate: Controlled-NOT — entangles two qubits
  - CZ gate: Controlled-Z — phase flip, used in Grover's oracle
  - Measurement: collapses superposition to a definite 0 or 1
  - Shots: how many times we run the circuit to build statistics
"""

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# ─────────────────────────────────────────────────────────────────────────────
# CIRCUIT BUILDERS
# Each function builds one QuantumCircuit and returns it.
# None of these run the circuit — running happens in run_circuit() below.
# ─────────────────────────────────────────────────────────────────────────────


def build_bell_circuit() -> QuantumCircuit:
    """
    Build the Bell State circuit — the "Hello World" of quantum computing.

    WHY IT MATTERS:
      Bell State is the simplest proof that quantum entanglement exists.
      Two qubits become correlated so that measuring one instantly
      determines the other. Einstein called this "spooky action at a distance."

    THE CIRCUIT (2 qubits, 2 classical bits for measurement):

        q0: ── H ── ●──  measure → c0
                    │
        q1: ─────── X──  measure → c1

    STEP BY STEP:
      1. Both qubits start in |0⟩ (all qubits always start at 0)
      2. H gate on q0 → q0 enters superposition: (|0⟩ + |1⟩)/√2
         System state: (|00⟩ + |10⟩)/√2
      3. CNOT (control=q0, target=q1) → creates entanglement
         When q0 was |0⟩: q1 stays |0⟩
         When q0 was |1⟩: q1 flips to |1⟩
         System state: (|00⟩ + |11⟩)/√2  ← this is the Bell State
      4. Measure both → collapse to either 00 or 11 with equal probability

    IDEAL RESULT (no noise, 1024 shots):
      '00': ~512    '11': ~512    '01': 0    '10': 0

    WITH NOISE:
      '01' and '10' start appearing — the entanglement is being disrupted.
      More noise = more '01' and '10' = more visible in our chart.
    """
    # QuantumCircuit(n_qubits, n_classical_bits)
    # Classical bits are needed to store measurement results
    circuit = QuantumCircuit(2, 2)

    # Step 1: Hadamard gate on qubit 0
    # Puts q0 into equal superposition: P(0) = 50%, P(1) = 50%
    circuit.h(0)

    # Step 2: CNOT gate — control=q0, target=q1
    # This "entangles" the two qubits.
    # cx(control_qubit_index, target_qubit_index)
    circuit.cx(0, 1)

    # Step 3: Measure both qubits into classical bits
    # measure(qubit_index, classical_bit_index)
    circuit.measure(0, 0)
    circuit.measure(1, 1)

    return circuit


def build_ghz_circuit() -> QuantumCircuit:
    """
    Build the GHZ (Greenberger-Horne-Zeilinger) State circuit.

    WHY IT MATTERS:
      GHZ extends Bell State to 3 qubits. All three qubits become
      entangled — measuring any one instantly determines the others.
      GHZ states are used in quantum error correction research and
      quantum networking experiments.

    THE CIRCUIT (3 qubits):

        q0: ── H ── ●────────  measure → c0
                    │
        q1: ─────── X ── ●──  measure → c1
                         │
        q2: ──────────── X──  measure → c2

    STEP BY STEP:
      1. H on q0 → superposition on q0
      2. CNOT(q0→q1) → entangles q0 and q1 (just like Bell State)
      3. CNOT(q1→q2) → extends entanglement chain to q2
         Now all 3 are correlated: if q0=0 then q1=0 and q2=0, etc.

    IDEAL RESULT (no noise, 1024 shots):
      '000': ~512    '111': ~512    everything else: 0

    WITH NOISE:
      States like '001', '010', '100', etc. start appearing.
      The 3-qubit entanglement is harder to maintain than 2-qubit — noise
      degrades GHZ faster than Bell State.
    """
    circuit = QuantumCircuit(3, 3)

    # Hadamard on q0 to start the entanglement chain
    circuit.h(0)

    # Entangle q0 → q1
    circuit.cx(0, 1)

    # Extend entanglement: q1 → q2
    # Now all three qubits are correlated
    circuit.cx(1, 2)

    # Measure all three qubits
    circuit.measure([0, 1, 2], [0, 1, 2])

    return circuit


def build_teleportation_circuit() -> QuantumCircuit:
    """
    Build the Quantum Teleportation circuit.

    WHY IT MATTERS:
      Quantum teleportation "transfers" a quantum state from one qubit to
      another using entanglement and classical communication. The original
      qubit's state is destroyed in the process (no-cloning theorem: you
      can't copy a quantum state). This is used in real quantum networks.

      IMPORTANT: This is NOT teleportation of matter — it's teleportation
      of quantum INFORMATION (the qubit's state).

    SETUP:
      q0 = the "message" qubit (we prepare it in |1⟩ — that's what we "send")
      q1 = Alice's half of an entangled pair (shared quantum channel)
      q2 = Bob's half of an entangled pair (destination)

    THE PROTOCOL:
      1. Prepare the message: q0 = |1⟩ (using X gate)
      2. Create entangled pair between q1 and q2 (like Bell State, but on q1,q2)
      3. Alice entangles her message qubit (q0) with her channel qubit (q1)
      4. Alice measures q0 and q1 → gets 2 classical bits
      5. Bob applies corrections to q2 based on Alice's 2 classical bits
      6. Result: q2 is now in state |1⟩ (what q0 started with)

    READING THE RESULTS:
      In Qiskit's output string "xyz": x=c[2]=q2, y=c[1]=q1, z=c[0]=q0
      (rightmost bit = lowest index qubit)

      States where leftmost bit = 1 (e.g., '100', '101', '110', '111')
      mean q2 was measured as |1⟩ → teleportation SUCCEEDED.

    IDEAL RESULT (no noise, 1024 shots):
      All states have '1' as their leftmost bit (q2=1):
      '100': ~256   '101': ~256   '110': ~256   '111': ~256

    WITH NOISE:
      Some states get '0' as leftmost bit (q2=0) — teleportation failed
      for those shots. More noise = q2=0 appears more often.
    """
    circuit = QuantumCircuit(3, 3)

    # ── STEP 1: Prepare the message qubit ──────────────────────────────────
    # We want to "teleport" the state |1⟩ from q0 to q2.
    # X gate flips |0⟩ → |1⟩ (like a classical NOT)
    circuit.x(0)

    # ── STEP 2: Create entangled pair (Alice's q1, Bob's q2) ───────────────
    # This is exactly a Bell State, but between q1 and q2 instead of q0 and q1.
    # Alice and Bob share this entangled pair as their "quantum channel."
    circuit.h(1)
    circuit.cx(1, 2)

    # ── STEP 3: Alice's operation — entangle message with her channel qubit ─
    circuit.cx(0, 1)   # CNOT: message q0 controls Alice's q1
    circuit.h(0)       # Hadamard on q0 (this is the "Bell measurement" step)

    # ── STEP 4: Alice measures her two qubits ──────────────────────────────
    # This destroys q0 and q1, but gives Alice 2 classical bits of information.
    circuit.measure(0, 0)  # q0 → classical bit c[0]
    circuit.measure(1, 1)  # q1 → classical bit c[1]

    # ── STEP 5: Bob applies corrections based on Alice's bits ──────────────
    # Bob can't see the quantum state directly (that would collapse it).
    # Instead, Alice tells Bob her measurement results via a classical channel
    # (phone call, email — any ordinary communication).
    # Bob then applies correction gates to q2:

    # If c[1] = 1 (Alice's q1 was measured as 1), Bob flips q2
    with circuit.if_test((circuit.clbits[1], 1)):
        circuit.x(2)

    # If c[0] = 1 (Alice's q0 was measured as 1), Bob phase-flips q2
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.z(2)

    # After corrections, q2 is guaranteed to be in state |1⟩
    circuit.measure(2, 2)  # q2 → classical bit c[2]

    return circuit


def build_grover_circuit() -> QuantumCircuit:
    """
    Build Grover's Search Algorithm circuit (searching for marked state |11⟩).

    WHY IT MATTERS:
      Classical search: to find 1 item in N unsorted items, you check ~N/2 on average.
      Grover's algorithm: finds it in only √N checks.
      For our 2-qubit case (N=4 items), Grover's finds the answer in 1 iteration —
      while classical might need up to 3 checks.

    HOW IT WORKS (intuition):
      1. Start all 4 states (00, 01, 10, 11) in equal superposition (25% each)
      2. ORACLE: Mark the target state |11⟩ by flipping its phase (makes it negative)
      3. DIFFUSER: "Invert about average" — this amplifies the marked state's probability
      4. Measure → the marked state shows up ~100% of the time

    THE CIRCUIT (2 qubits, marking |11⟩ as the answer):

      Initialization:   H─────────
      Oracle:           CZ         (phase flip if both qubits = 1)
      Diffuser:         H─X─CZ─X─H  (amplitude amplification)

    IDEAL RESULT (no noise, 1024 shots):
      '11': 1024   (100%!) — Grover's is perfect for 2 qubits with 1 iteration
      '00': 0    '01': 0    '10': 0

    WITH NOISE:
      Probability of '11' drops. With high noise, the algorithm fails to find
      the answer reliably — you might get wrong answers more often.
      This dramatically shows how quantum algorithms depend on low-noise hardware.
    """
    circuit = QuantumCircuit(2, 2)

    # ── STEP 1: Initialize — equal superposition ────────────────────────────
    # Apply H to both qubits: each has 25% probability of being 00, 01, 10, 11
    circuit.h(0)
    circuit.h(1)

    # ── STEP 2: Oracle — mark the target state |11⟩ ────────────────────────
    # CZ gate: applies a phase flip ONLY when BOTH qubits are |1⟩
    # This "marks" |11⟩ by flipping its sign: |11⟩ → -|11⟩
    # You can't see the phase flip directly in measurement, but the diffuser uses it.
    circuit.cz(0, 1)

    # ── STEP 3: Diffuser — amplify the marked state ─────────────────────────
    # The diffuser is sometimes called "inversion about average."
    # It takes all amplitudes, reflects them around their mean.
    # Since |11⟩ has a negative amplitude (from oracle), it ends up much larger
    # than the others after reflection. The math works out to ~100% probability.

    # Diffuser = H → X → CZ → X → H  (on both qubits)
    circuit.h([0, 1])     # un-compute superposition
    circuit.x([0, 1])     # flip all bits (shifts which state is "special")
    circuit.cz(0, 1)      # phase flip the |00⟩ state (which is our marked state now)
    circuit.x([0, 1])     # un-flip
    circuit.h([0, 1])     # re-create superposition — now |11⟩ has ~100% amplitude

    # ── STEP 4: Measure ─────────────────────────────────────────────────────
    circuit.measure([0, 1], [0, 1])

    return circuit


# ─────────────────────────────────────────────────────────────────────────────
# RUNNER
# ─────────────────────────────────────────────────────────────────────────────


def run_circuit(circuit: QuantumCircuit, shots: int = 1024, noise_model=None) -> dict:
    """
    Execute a quantum circuit on the Aer simulator and return measurement counts.

    WHY AER:
      AerSimulator is a classical CPU program that pretends to be a quantum computer.
      It simulates the mathematics of quantum mechanics exactly.
      Without it, you'd need access to IBM's real quantum hardware.

    Args:
        circuit:     A QuantumCircuit built by one of our build_*() functions.
        shots:       How many times to run the circuit.
                     More shots = more accurate probability estimates.
                     1024 shots gives ±3% statistical uncertainty.
        noise_model: Optional NoiseModel from noise_models.py.
                     None = perfect simulation (ideal quantum computer).
                     Provided = depolarizing errors on each gate.

    Returns:
        dict mapping measurement outcome → count.
        e.g. {'00': 487, '01': 26, '10': 19, '11': 492}

    WHY TRANSPILE:
        Qiskit circuits are written in a "universal" gate set.
        transpile() converts them to the specific gates the simulator understands.
        Think of it like a compiler — your high-level code → machine code.
    """
    simulator = AerSimulator()

    # transpile: convert circuit to simulator's native gate set
    compiled_circuit = transpile(circuit, simulator)

    # Run the simulation
    if noise_model is not None:
        job = simulator.run(compiled_circuit, shots=shots, noise_model=noise_model)
    else:
        job = simulator.run(compiled_circuit, shots=shots)

    # Extract results
    # get_counts() returns {measurement_string: number_of_times_it_occurred}
    counts = job.result().get_counts(compiled_circuit)

    # Convert from Qiskit's Counter type to plain dict for JSON serialization
    return dict(counts)


# ─────────────────────────────────────────────────────────────────────────────
# DISPATCHER
# The single entry point Flask calls — maps circuit names to builder functions.
# ─────────────────────────────────────────────────────────────────────────────

# Maps the string name (from the API) to the function that builds that circuit.
# When Flask receives POST /api/simulate with {"circuit": "bell"}, it calls
# run_named_circuit("bell", ...) which looks up CIRCUIT_BUILDERS["bell"] and runs it.
CIRCUIT_BUILDERS = {
    "bell":          build_bell_circuit,
    "ghz":           build_ghz_circuit,
    "teleportation": build_teleportation_circuit,
    "grover":        build_grover_circuit,
}

# Ideal (no-noise) measurement distributions for each circuit.
# Used to draw the "reference" bars in our comparison chart.
# The fractions are the theoretical probabilities × shots.
IDEAL_DISTRIBUTIONS = {
    "bell":          {"00": 0.5,   "11": 0.5},
    "ghz":           {"000": 0.5,  "111": 0.5},
    # Teleportation: q0 sent |1>, so q2 (leftmost bit) should be 1.
    # Alice's q0, q1 are random (25% each combination).
    "teleportation": {"100": 0.25, "101": 0.25, "110": 0.25, "111": 0.25},
    "grover":        {"11": 1.0},
}


def run_named_circuit(circuit_name: str, error_rate: float, shots: int = 1024) -> dict:
    """
    Main entry point: build and simulate a named circuit with optional noise.

    This is the function Flask calls. It:
      1. Validates the circuit name
      2. Builds the Qiskit circuit
      3. Builds the noise model (imported here to avoid circular imports)
      4. Runs the simulation
      5. Returns the measurement counts

    Args:
        circuit_name: 'bell', 'ghz', 'teleportation', or 'grover'
        error_rate:   0.0 (no noise) to 0.20 (20% error per gate)
        shots:        Number of simulation runs (default 1024)

    Returns:
        dict: {state_string: count}, e.g. {'00': 487, '11': 537}

    Raises:
        ValueError: if circuit_name is not in CIRCUIT_BUILDERS
    """
    if circuit_name not in CIRCUIT_BUILDERS:
        valid = list(CIRCUIT_BUILDERS.keys())
        raise ValueError(
            f"Unknown circuit '{circuit_name}'. Valid options: {valid}"
        )

    # Build the Qiskit circuit object
    circuit = CIRCUIT_BUILDERS[circuit_name]()

    # Build the noise model (import here to avoid issues if noise_models isn't ready)
    # noise_model will be None when error_rate == 0.0 → perfect simulation
    try:
        from noise_models import build_noise_model
        noise_model = build_noise_model(error_rate)
    except ImportError:
        # noise_models.py not yet created — run ideal simulation
        noise_model = None

    # Run the simulation and return counts
    return run_circuit(circuit, shots=shots, noise_model=noise_model)


def get_ideal_counts(circuit_name: str, shots: int) -> dict:
    """
    Return the theoretical ideal measurement distribution for a circuit.

    Used by the Flask API to include reference "ideal" bars in the chart,
    so users can visually compare their noisy result against the perfect case.

    Args:
        circuit_name: 'bell', 'ghz', 'teleportation', or 'grover'
        shots:        Total shots (used to scale probabilities to counts)

    Returns:
        dict: {state: count} for ideal results.
              e.g. for bell with 1024 shots: {'00': 512, '11': 512}
    """
    if circuit_name not in IDEAL_DISTRIBUTIONS:
        return {}

    # Multiply each probability by shots to get expected count
    return {
        state: int(prob * shots)
        for state, prob in IDEAL_DISTRIBUTIONS[circuit_name].items()
    }


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL TEST — run this file directly to see all circuits work
# Command: python backend/quantum_engine.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    SHOTS = 1024

    print("=" * 60)
    print("Quantum Engine — Manual Test")
    print("Running all 4 circuits with NO noise (ideal)")
    print("=" * 60)

    for name in CIRCUIT_BUILDERS:
        print(f"\n[ {name.upper()} ]")
        counts = run_named_circuit(name, error_rate=0.0, shots=SHOTS)
        ideal  = get_ideal_counts(name, SHOTS)

        # Sort states alphabetically for clean output
        for state in sorted(counts):
            bar = "█" * (counts[state] // 20)  # simple ASCII bar chart
            print(f"  |{state}⟩  {counts[state]:4d}  {bar}")

        print(f"  Ideal: {ideal}")

    print("\n" + "=" * 60)
    print("Running BELL STATE with increasing noise levels:")
    print("=" * 60)
    for p in [0.0, 0.05, 0.10, 0.20]:
        counts = run_named_circuit("bell", error_rate=p, shots=SHOTS)
        error_count = counts.get("01", 0) + counts.get("10", 0)
        print(f"  p={p:.2f}  errors={error_count:3d}/{SHOTS}  counts={counts}")

    print("\nAll circuits OK!")
