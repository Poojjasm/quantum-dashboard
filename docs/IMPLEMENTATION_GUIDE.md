# Implementation Guide — Phase-by-Phase Build Instructions

> This is your step-by-step construction manual.
> Work through it in order. Don't skip phases — each one builds on the last.

---

## Before You Code: The Golden Rule

**Build → Test → Commit → Move On**

Never write more than ~50 lines of new code without testing it.
If something breaks, you want to know immediately — not after 300 lines.

---

## WEEK 1: BACKEND

---

## Phase 1: Quantum Engine (Days 1-2)

**Goal:** A Python file that can run all 4 circuits and return measurement counts.
**File to create:** `backend/quantum_engine.py`
**Test:** Run `python backend/quantum_engine.py` and see output in terminal.

### Concepts to understand first
Read `QUANTUM_CONCEPTS.md` completely before starting this phase.
Key things to know: qubits, superposition, entanglement, H gate, CNOT gate.

### Step 1.1 — Install Qiskit and verify

```bash
# Activate your virtual environment first!
source venv/bin/activate

# Install
pip install qiskit qiskit-aer

# Verify — open Python REPL
python3 -c "import qiskit; print(qiskit.__version__)"
# Should print something like: 0.45.3
```

### Step 1.2 — Write your first circuit (Bell State)

```python
# backend/quantum_engine.py

from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

def build_bell_circuit():
    """
    Build the Bell State quantum circuit.

    A Bell State is the simplest example of quantum entanglement.
    Two qubits become correlated — measuring one instantly determines the other.

    Circuit:
        q0: ── H ── ●──  measure
                    │
        q1: ─────── X──  measure

    Returns:
        QuantumCircuit: The Bell State circuit ready to simulate
    """
    # Create a circuit with 2 qubits and 2 classical bits (for measurement results)
    circuit = QuantumCircuit(2, 2)

    # Step 1: Apply Hadamard gate to qubit 0
    # This puts q0 into superposition: 50% chance of 0, 50% chance of 1
    circuit.h(0)

    # Step 2: Apply CNOT gate (control=q0, target=q1)
    # This entangles the two qubits
    # If q0=0 → q1 stays 0. If q0=1 → q1 flips to 1.
    # Result: (|00⟩ + |11⟩) / √2  (the Bell State)
    circuit.cx(0, 1)

    # Step 3: Measure both qubits into classical bits
    # circuit.measure(qubit_index, classical_bit_index)
    circuit.measure(0, 0)
    circuit.measure(1, 1)

    return circuit


def run_circuit(circuit, shots=1024, noise_model=None):
    """
    Run a quantum circuit simulation.

    Args:
        circuit: A QuantumCircuit object built by one of our build_* functions
        shots: How many times to run the circuit (more = more accurate statistics)
        noise_model: Optional NoiseModel object. None = ideal, no noise.

    Returns:
        dict: Measurement counts, e.g. {"00": 512, "11": 512}
    """
    # AerSimulator is a classical CPU that simulates quantum behavior
    simulator = AerSimulator()

    # Run the simulation
    # transpile converts our circuit to the simulator's gate set
    from qiskit import transpile
    compiled = transpile(circuit, simulator)

    if noise_model:
        job = simulator.run(compiled, shots=shots, noise_model=noise_model)
    else:
        job = simulator.run(compiled, shots=shots)

    # Get results
    result = job.result()
    counts = result.get_counts(compiled)

    return counts


# Test it directly
if __name__ == "__main__":
    circuit = build_bell_circuit()
    print("Circuit diagram:")
    print(circuit.draw())

    counts = run_circuit(circuit, shots=1024)
    print(f"\nResults (1024 shots): {counts}")
    # Expected: {'00': ~512, '11': ~512}
```

Run it: `python backend/quantum_engine.py`

### Step 1.3 — Add the remaining 3 circuits

```python
def build_ghz_circuit():
    """
    GHZ State: 3-qubit entangled state.
    Named after Greenberger, Horne, Zeilinger (1989).

    Circuit:
        q0: ── H ── ●────────  measure
                    │
        q1: ─────── X ── ●──  measure
                         │
        q2: ──────────── X──  measure

    Ideal result: 50% |000⟩, 50% |111⟩
    """
    circuit = QuantumCircuit(3, 3)

    circuit.h(0)            # superposition on q0
    circuit.cx(0, 1)        # entangle q0 → q1
    circuit.cx(1, 2)        # extend entanglement to q2

    circuit.measure([0, 1, 2], [0, 1, 2])
    return circuit


def build_teleportation_circuit():
    """
    Quantum Teleportation: transfer a quantum state using entanglement.

    q0 = message qubit (we'll put it in state |+⟩ = (|0⟩+|1⟩)/√2)
    q1 = Alice's entangled qubit
    q2 = Bob's entangled qubit (should end up matching q0 after protocol)

    Ideal result: q2 ends up in the same state q0 started in.
    """
    circuit = QuantumCircuit(3, 3)

    # Prepare the message qubit in an interesting state
    circuit.h(0)           # q0 → superposition (the state we're "teleporting")

    # Create entangled pair between q1 and q2 (Alice and Bob share this)
    circuit.h(1)
    circuit.cx(1, 2)

    # Alice's operations: entangle message qubit with her half of the pair
    circuit.cx(0, 1)
    circuit.h(0)

    # Alice measures her qubits (collapses them, gets 2 classical bits)
    circuit.measure(0, 0)
    circuit.measure(1, 1)

    # Bob applies corrections based on Alice's measurement results
    # (classically controlled quantum gates)
    with circuit.if_test((circuit.clbits[1], 1)):
        circuit.x(2)       # if Alice's q1 was 1, flip Bob's qubit
    with circuit.if_test((circuit.clbits[0], 1)):
        circuit.z(2)       # if Alice's q0 was 1, phase-flip Bob's qubit

    circuit.measure(2, 2)
    return circuit


def build_grover_circuit():
    """
    Grover's Algorithm: quantum search for marked state |11⟩.

    Finds the marked item quadratically faster than classical search.
    For 4 items (2 qubits), Grover needs only 1 iteration.

    Ideal result: |11⟩ appears ~95%+ of the time.
    """
    circuit = QuantumCircuit(2, 2)

    # Step 1: Initialize — put all states in equal superposition
    circuit.h(0)
    circuit.h(1)

    # Step 2: Oracle — mark the target state |11⟩ with a phase flip
    # CZ flips the phase of |11⟩ specifically
    circuit.cz(0, 1)

    # Step 3: Diffuser — amplify the marked state's probability
    circuit.h(0)
    circuit.h(1)
    circuit.x(0)
    circuit.x(1)
    circuit.cz(0, 1)
    circuit.x(0)
    circuit.x(1)
    circuit.h(0)
    circuit.h(1)

    circuit.measure([0, 1], [0, 1])
    return circuit
```

### What "done" looks like for Phase 1
Run this and see sensible output:
```bash
python backend/quantum_engine.py
# Bell:          {'00': ~512, '11': ~512}
# GHZ:           {'000': ~512, '111': ~512}
# Teleportation: should show '1' for q2 most of the time
# Grover:        {'11': ~976, rest small}
```

### Git commit for Phase 1
```bash
git add backend/quantum_engine.py
git commit -m "feat: implement 4 quantum circuits with Qiskit"
```

---

## Phase 2: Noise Models (Days 3-4)

**Goal:** Add depolarizing noise to any circuit at any error rate.
**File to create:** `backend/noise_models.py`
**Test:** Run Bell State with p=0.1 and see "01" and "10" appear.

### Concepts to understand first
Read the "Quantum Errors and Noise" section in `QUANTUM_CONCEPTS.md`.
Key concept: depolarizing error model, what `p` means.

### Step 2.1 — Build the noise model

```python
# backend/noise_models.py

from qiskit_aer.noise import (
    NoiseModel,
    depolarizing_error,
)


def build_noise_model(error_rate: float) -> NoiseModel | None:
    """
    Build a depolarizing noise model for quantum circuit simulation.

    What is depolarizing noise?
    With probability p, each gate fails and applies a random error (X, Y, or Z).
    With probability (1-p), the gate works perfectly.

    Args:
        error_rate: float between 0.0 and 0.20
                    0.0 = perfect, no noise
                    0.05 = 5% chance of error per gate
                    0.20 = 20% chance of error per gate

    Returns:
        NoiseModel if error_rate > 0, else None (perfect simulation)
    """
    if error_rate == 0.0:
        # No noise — return None to skip the noise model entirely
        return None

    noise_model = NoiseModel()

    # Single-qubit gate error (H, X, Z gates)
    # These errors are less severe than 2-qubit errors
    single_qubit_error = depolarizing_error(error_rate, 1)

    # Two-qubit gate error (CNOT/CX, CZ gates)
    # In real quantum computers, 2-qubit gates are ~10x more error-prone
    # We model this with a slightly higher rate
    two_qubit_error = depolarizing_error(min(error_rate * 2, 1.0), 2)

    # Apply 1-qubit errors to all single-qubit gates
    noise_model.add_all_qubit_quantum_error(
        single_qubit_error,
        ['h', 'x', 'y', 'z', 's', 't']  # single-qubit gate names in Qiskit
    )

    # Apply 2-qubit errors to all two-qubit gates
    noise_model.add_all_qubit_quantum_error(
        two_qubit_error,
        ['cx', 'cz']  # CNOT and CZ gate names
    )

    return noise_model


def get_ideal_counts(circuit_name: str, shots: int) -> dict:
    """
    Return the theoretical ideal measurement distribution for a circuit.
    Used to show the "perfect" reference bars in our chart.

    Args:
        circuit_name: 'bell', 'ghz', 'teleportation', or 'grover'
        shots: total number of shots (for scaling counts)

    Returns:
        dict of {state: count} for ideal results
    """
    half = shots // 2

    ideal_distributions = {
        "bell": {
            "00": half,
            "11": shots - half,
        },
        "ghz": {
            "000": half,
            "111": shots - half,
        },
        "teleportation": {
            # After teleportation, q2 should match q0's initial state
            # q0 started in |+⟩, so q2 ends in |+⟩ → 50/50 on q2
            "0": half,
            "1": shots - half,
        },
        "grover": {
            # Grover marks |11⟩, so ideally it appears ~96% of the time
            "11": int(shots * 0.96),
            "00": int(shots * 0.013),
            "01": int(shots * 0.013),
            "10": int(shots * 0.014),
        },
    }

    return ideal_distributions.get(circuit_name, {})
```

### Step 2.2 — Update quantum_engine.py to use noise

Add a main dispatcher function to `quantum_engine.py`:

```python
# Add this to backend/quantum_engine.py

from noise_models import build_noise_model

# Map circuit names to their builder functions
CIRCUIT_BUILDERS = {
    "bell": build_bell_circuit,
    "ghz": build_ghz_circuit,
    "teleportation": build_teleportation_circuit,
    "grover": build_grover_circuit,
}

def run_named_circuit(circuit_name: str, error_rate: float, shots: int = 1024) -> dict:
    """
    Main entry point: build and run a named circuit with optional noise.

    This is the function Flask will call.

    Args:
        circuit_name: 'bell', 'ghz', 'teleportation', or 'grover'
        error_rate: 0.0 to 0.20 depolarizing error rate
        shots: number of simulation runs

    Returns:
        dict: measurement counts, e.g. {'00': 467, '01': 28, '10': 22, '11': 507}

    Raises:
        ValueError: if circuit_name is not recognized
    """
    if circuit_name not in CIRCUIT_BUILDERS:
        raise ValueError(
            f"Unknown circuit: '{circuit_name}'. "
            f"Valid options: {list(CIRCUIT_BUILDERS.keys())}"
        )

    # Build the circuit
    circuit = CIRCUIT_BUILDERS[circuit_name]()

    # Build the noise model (or None if error_rate == 0)
    noise_model = build_noise_model(error_rate)

    # Run simulation
    counts = run_circuit(circuit, shots=shots, noise_model=noise_model)

    return counts
```

### What "done" looks like for Phase 2
```python
# Quick test in Python REPL:
from quantum_engine import run_named_circuit

# Bell State with no noise — should be near-perfect
print(run_named_circuit("bell", 0.0))
# Expected: {'00': ~512, '11': ~512}

# Bell State with 10% noise — should show errors
print(run_named_circuit("bell", 0.1))
# Expected: {'00': ~420, '01': ~50, '10': ~50, '11': ~504} (roughly)
```

### Git commit for Phase 2
```bash
git add backend/noise_models.py backend/quantum_engine.py
git commit -m "feat: add depolarizing noise models to all circuits"
```

---

## Phase 3: Database (Days 4-5)

**Goal:** Store simulation results in SQLite so we can retrieve history.
**File to create:** `backend/database.py`
**Test:** Insert a simulation, then query it back.

### Concepts to understand first
Read `DATABASE_SCHEMA.md` for the table design.
Key concepts: primary keys, foreign keys, SQL CRUD (Create, Read, Update, Delete).

### Step 3.1 — Build database.py

```python
# backend/database.py

import sqlite3
import os
from datetime import datetime

# Database file path — relative to project root
# Using data/ folder which is git-ignored
DB_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),  # go up to project root
    "data",
    "quantum_circuits.db"
)


def get_connection():
    """
    Open a connection to the SQLite database.
    SQLite is file-based — the .db file IS the database.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row   # Makes rows dict-like: row['column_name']
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key enforcement
    return conn


def init_db():
    """
    Create all tables if they don't exist yet.
    Safe to call every time — CREATE TABLE IF NOT EXISTS won't overwrite.
    Call this once when the Flask app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create circuits table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS circuits (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT,
            num_qubits  INTEGER NOT NULL,
            difficulty  TEXT DEFAULT 'beginner'
        )
    """)

    # Create simulations table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id  TEXT NOT NULL,
            error_rate  REAL NOT NULL,
            shots       INTEGER NOT NULL,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (circuit_id) REFERENCES circuits(id)
        )
    """)

    # Create results table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER NOT NULL,
            state         TEXT NOT NULL,
            count         INTEGER NOT NULL,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
                ON DELETE CASCADE
        )
    """)

    # Seed the circuits table with our 4 circuits
    seed_circuits(cursor)

    conn.commit()
    conn.close()


def seed_circuits(cursor):
    """
    Insert the 4 circuit definitions into the circuits table.
    Uses INSERT OR IGNORE so re-running won't duplicate.
    """
    circuits = [
        ("bell", "Bell State",
         "Creates a maximally entangled 2-qubit state.", 2, "beginner"),
        ("ghz", "GHZ State",
         "3-qubit generalized entangled state.", 3, "beginner"),
        ("teleportation", "Quantum Teleportation",
         "Transfers quantum state using entanglement.", 3, "intermediate"),
        ("grover", "Grover's Algorithm",
         "Quantum search: finds marked state quadratically faster.", 2, "intermediate"),
    ]

    cursor.executemany(
        "INSERT OR IGNORE INTO circuits VALUES (?, ?, ?, ?, ?)",
        circuits
    )


def save_simulation(circuit_id: str, error_rate: float, shots: int, counts: dict) -> int:
    """
    Save a simulation run and its measurement results to the database.

    Args:
        circuit_id: 'bell', 'ghz', 'teleportation', or 'grover'
        error_rate: the noise level used
        shots: number of simulation runs
        counts: dict like {'00': 512, '11': 512}

    Returns:
        int: The ID of the newly created simulation row
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Insert simulation record
    cursor.execute(
        "INSERT INTO simulations (circuit_id, error_rate, shots) VALUES (?, ?, ?)",
        (circuit_id, error_rate, shots)
    )
    simulation_id = cursor.lastrowid  # Get the auto-assigned ID

    # Insert one results row per measurement outcome
    for state, count in counts.items():
        cursor.execute(
            "INSERT INTO results (simulation_id, state, count) VALUES (?, ?, ?)",
            (simulation_id, state, count)
        )

    conn.commit()
    conn.close()

    return simulation_id


def get_simulation(simulation_id: int) -> dict | None:
    """
    Retrieve a simulation and its results by ID.

    Returns:
        dict with 'simulation' and 'results' keys, or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Get the simulation metadata
    cursor.execute(
        """
        SELECT s.id, c.id as circuit_id, c.name as circuit_name,
               s.error_rate, s.shots, s.created_at
        FROM simulations s
        JOIN circuits c ON s.circuit_id = c.id
        WHERE s.id = ?
        """,
        (simulation_id,)
    )
    sim_row = cursor.fetchone()

    if sim_row is None:
        conn.close()
        return None

    # Get the measurement results
    cursor.execute(
        "SELECT state, count FROM results WHERE simulation_id = ? ORDER BY state",
        (simulation_id,)
    )
    result_rows = cursor.fetchall()

    conn.close()

    return {
        "simulation": dict(sim_row),
        "results": [dict(row) for row in result_rows],
    }


def get_history(limit: int = 20, circuit_filter: str = None) -> list:
    """
    Get the most recent simulations.

    Args:
        limit: max number to return
        circuit_filter: optional circuit ID to filter by

    Returns:
        list of simulation dicts
    """
    conn = get_connection()
    cursor = conn.cursor()

    if circuit_filter:
        cursor.execute(
            """
            SELECT s.id, c.name as circuit_name, s.error_rate,
                   s.shots, s.created_at
            FROM simulations s
            JOIN circuits c ON s.circuit_id = c.id
            WHERE s.circuit_id = ?
            ORDER BY s.created_at DESC
            LIMIT ?
            """,
            (circuit_filter, limit)
        )
    else:
        cursor.execute(
            """
            SELECT s.id, c.name as circuit_name, s.error_rate,
                   s.shots, s.created_at
            FROM simulations s
            JOIN circuits c ON s.circuit_id = c.id
            ORDER BY s.created_at DESC
            LIMIT ?
            """,
            (limit,)
        )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]
```

### Git commit for Phase 3
```bash
git add backend/database.py
git commit -m "feat: implement SQLite database schema and CRUD operations"
```

---

## Phase 4: Flask API (Days 6-7)

**Goal:** HTTP endpoints that connect the frontend to the quantum engine.
**File to create:** `backend/app.py`
**Test:** curl commands against each endpoint.

### Concepts to understand first
Read `API_REFERENCE.md` for the complete endpoint specification.
Key concepts: HTTP methods (GET/POST), JSON, status codes, REST.

### Step 4.1 — Build app.py

```python
# backend/app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
import os

# Add backend directory to Python path so we can import our modules
sys.path.insert(0, os.path.dirname(__file__))

from quantum_engine import run_named_circuit, CIRCUIT_BUILDERS
from noise_models import get_ideal_counts
from database import init_db, save_simulation, get_simulation, get_history

app = Flask(__name__)
CORS(app)  # Allow the browser to call our API from any origin

# Initialize database on startup
init_db()

VALID_CIRCUITS = list(CIRCUIT_BUILDERS.keys())


@app.route("/api/circuits", methods=["GET"])
def get_circuits():
    """Return list of all available quantum circuits."""
    circuits = [
        {
            "id": "bell",
            "name": "Bell State",
            "description": "Creates a maximally entangled 2-qubit state. The simplest demonstration of quantum entanglement.",
            "num_qubits": 2,
            "difficulty": "beginner",
        },
        {
            "id": "ghz",
            "name": "GHZ State",
            "description": "3-qubit entangled state. Extends Bell State to three qubits.",
            "num_qubits": 3,
            "difficulty": "beginner",
        },
        {
            "id": "teleportation",
            "name": "Quantum Teleportation",
            "description": "Transfers a quantum state from one qubit to another using entanglement.",
            "num_qubits": 3,
            "difficulty": "intermediate",
        },
        {
            "id": "grover",
            "name": "Grover's Algorithm",
            "description": "Quantum search algorithm. Finds a marked item quadratically faster than classical search.",
            "num_qubits": 2,
            "difficulty": "intermediate",
        },
    ]
    return jsonify({"circuits": circuits})


@app.route("/api/simulate", methods=["POST"])
def simulate():
    """
    Run a quantum circuit simulation.

    Expected JSON body:
        {
            "circuit": "bell",        (required)
            "error_rate": 0.05,       (required, 0.0-0.20)
            "shots": 1024             (optional, default 1024)
        }
    """
    data = request.get_json()

    # --- Input validation ---
    if not data:
        return jsonify({"error": "Request body must be JSON", "code": "BAD_REQUEST"}), 400

    circuit_name = data.get("circuit")
    if not circuit_name:
        return jsonify({"error": "circuit is required", "code": "MISSING_FIELD"}), 400

    if circuit_name not in VALID_CIRCUITS:
        return jsonify({
            "error": f"Invalid circuit. Must be one of: {VALID_CIRCUITS}",
            "code": "INVALID_CIRCUIT"
        }), 400

    error_rate = data.get("error_rate")
    if error_rate is None:
        return jsonify({"error": "error_rate is required", "code": "MISSING_FIELD"}), 400

    try:
        error_rate = float(error_rate)
    except (ValueError, TypeError):
        return jsonify({"error": "error_rate must be a number", "code": "INVALID_TYPE"}), 400

    if not (0.0 <= error_rate <= 0.20):
        return jsonify({
            "error": "error_rate must be between 0.0 and 0.20",
            "code": "OUT_OF_RANGE"
        }), 422

    shots = int(data.get("shots", 1024))
    shots = max(100, min(8192, shots))  # Clamp to valid range

    # --- Run simulation ---
    try:
        counts = run_named_circuit(circuit_name, error_rate, shots)
    except Exception as e:
        return jsonify({
            "error": f"Simulation failed: {str(e)}",
            "code": "SIMULATION_ERROR"
        }), 500

    # --- Save to database ---
    simulation_id = save_simulation(circuit_name, error_rate, shots, counts)

    # --- Build response ---
    ideal = get_ideal_counts(circuit_name, shots)

    return jsonify({
        "simulation_id": simulation_id,
        "circuit": circuit_name,
        "error_rate": error_rate,
        "shots": shots,
        "counts": counts,
        "ideal_counts": ideal,
    })


@app.route("/api/results/<int:simulation_id>", methods=["GET"])
def get_results(simulation_id):
    """Retrieve a past simulation by ID."""
    data = get_simulation(simulation_id)

    if data is None:
        return jsonify({
            "error": f"Simulation {simulation_id} not found",
            "code": "NOT_FOUND"
        }), 404

    return jsonify(data)


@app.route("/api/history", methods=["GET"])
def history():
    """Return recent simulation history."""
    limit = request.args.get("limit", 20, type=int)
    circuit = request.args.get("circuit")

    simulations = get_history(limit=limit, circuit_filter=circuit)
    return jsonify({"simulations": simulations, "total": len(simulations)})


if __name__ == "__main__":
    # debug=True auto-reloads when you save files — very useful for development
    app.run(debug=True, port=5000)
```

### Test with curl

```bash
# Start the server first (in one terminal):
python backend/app.py

# In another terminal:

# Test 1: Get circuits list
curl http://localhost:5000/api/circuits

# Test 2: Run a Bell State simulation
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.05, "shots": 1024}'

# Test 3: Get simulation by ID (use the ID from Test 2's response)
curl http://localhost:5000/api/results/1

# Test 4: Error handling — invalid circuit
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "invalid", "error_rate": 0.05}'
```

### Git commit for Phase 4
```bash
git add backend/app.py
git commit -m "feat: create Flask REST API with 4 endpoints"
```

---

## WEEK 2: FRONTEND

> Detailed frontend code templates are in the Phase 5-8 sections.
> For now, review the structure and plan your approach.

---

## Phase 5-8 Preview: Frontend Structure

```
frontend/
├── index.html           ← Phase 5
└── static/
    ├── js/
    │   └── app.js       ← Phase 6 + 7
    └── css/
        └── styles.css   ← Phase 8
```

**Phase 5 (HTML):** Build the skeleton — circuit selector, error slider, button, chart canvas, history panel.

**Phase 6 (JavaScript):** Wire everything up — click handlers, fetch() calls to Flask, DOM updates, loading states.

**Phase 7 (Chart.js):** Render the results — bar chart with ideal vs noisy bars, labels, colors.

**Phase 8 (CSS):** Make it look professional — dark theme, responsive grid, hover effects.

> Full templates for phases 5-8 will be provided when you reach Week 2.

---

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---|---|---|
| Forgot `venv` | `ImportError: No module named qiskit` | `source venv/bin/activate` |
| Wrong working directory | `ModuleNotFoundError` | Run from project root |
| DB not initialized | `OperationalError: no such table` | `init_db()` in `app.py` startup |
| CORS blocked | Browser console: "CORS error" | Add `flask-cors` to `app.py` |
| Missing `measure()` | Empty counts dict `{}` | Add `circuit.measure_all()` |
| Classical bits mismatch | Wrong number of bits in result string | `QuantumCircuit(n_qubits, n_qubits)` |
