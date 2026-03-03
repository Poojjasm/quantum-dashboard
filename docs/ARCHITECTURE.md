# System Architecture — Quantum Circuit Error Analyzer

## Overview

This is a 3-tier web application:
1. **Frontend** (browser) — what the user sees and interacts with
2. **Backend** (Flask API) — processes requests, orchestrates everything
3. **Data layer** (Qiskit + SQLite) — runs simulations, stores results

Each tier communicates through well-defined interfaces: HTTP/JSON between frontend and backend,
Python function calls between backend and quantum engine, and SQL between backend and database.

---

## Component Interaction Diagram

```
╔══════════════════════════════════════════════════════════════════╗
║                         USER'S BROWSER                           ║
║                                                                  ║
║  ┌──────────────────────────────────────────────────────────┐   ║
║  │                    index.html                             │   ║
║  │  ┌──────────────┐  ┌────────────────┐  ┌─────────────┐  │   ║
║  │  │Circuit select│  │ Error rate      │  │  [Simulate] │  │   ║
║  │  │  dropdown    │  │ slider 0-20%   │  │   button    │  │   ║
║  │  └──────────────┘  └────────────────┘  └──────┬──────┘  │   ║
║  │                                                │          │   ║
║  │  ┌─────────────────────────────────────────┐  │          │   ║
║  │  │           Chart.js Canvas               │  │          │   ║
║  │  │     (bar chart: measurement counts)     │  │          │   ║
║  │  └─────────────────────────────────────────┘  │          │   ║
║  └──────────────────────────────────────────┬────┘          ║   ║
║                    app.js                   │               ║   ║
╚════════════════════════════════════════════╪════════════════╝   ║
                                             │
                         fetch() POST /api/simulate
                         { circuit, error_rate, shots }
                                             │
                                             ▼
╔══════════════════════════════════════════════════════════════════╗
║                      FLASK BACKEND (app.py)                      ║
║                                                                  ║
║   Receives request → validates input → calls quantum engine      ║
║   → saves to database → returns JSON response                    ║
║                                                                  ║
║   Routes:                                                        ║
║   GET  /api/circuits    → returns circuit list                   ║
║   POST /api/simulate    → runs simulation                        ║
║   GET  /api/results/id  → fetches past simulation                ║
╚══════════╤════════════════════════════╤═══════════════════════════╝
           │                            │
   calls   │                    saves   │
           ▼                            ▼
╔═══════════════════╗        ╔══════════════════════╗
║  QUANTUM ENGINE   ║        ║   SQLite Database    ║
║                   ║        ║                      ║
║ quantum_engine.py ║        ║  circuits table      ║
║ noise_models.py   ║        ║  simulations table   ║
║                   ║        ║  results table       ║
║ Qiskit + Aer      ║        ║                      ║
║ (runs simulation) ║        ║  (persistent storage)║
╚═══════════════════╝        ╚══════════════════════╝
```

---

## Data Flow — Step by Step

### When User Clicks "Simulate"

```
Step 1  User selects "Bell State", sets error_rate=0.05, clicks Simulate

Step 2  app.js reads form values:
        circuit = "bell"
        error_rate = 0.05
        shots = 1024

Step 3  app.js sends HTTP POST to Flask:
        POST /api/simulate
        Content-Type: application/json
        Body: {"circuit": "bell", "error_rate": 0.05, "shots": 1024}

Step 4  Flask app.py receives request:
        - Validates circuit name ("bell" is valid ✓)
        - Validates error_rate (0.05 is in range ✓)
        - Calls: quantum_engine.run_circuit("bell", 0.05, 1024)

Step 5  quantum_engine.py:
        - Builds Bell State circuit (H gate + CNOT gate)
        - Calls: noise_models.build_noise_model(0.05)

Step 6  noise_models.py:
        - Creates depolarizing noise model with p=0.05
        - Returns NoiseModel object

Step 7  quantum_engine.py (continued):
        - Runs Qiskit AerSimulator with noise model, 1024 shots
        - Returns: {"00": 467, "01": 28, "10": 22, "11": 507}

Step 8  Flask app.py (continued):
        - Calls: database.save_simulation("bell", 0.05, 1024, counts)
        - Database inserts row into simulations table
        - Database inserts rows into results table (one per state)
        - Returns simulation_id = 42

Step 9  Flask sends HTTP response:
        200 OK
        {
          "simulation_id": 42,
          "circuit": "bell",
          "error_rate": 0.05,
          "counts": {"00": 467, "01": 28, "10": 22, "11": 507},
          "ideal_counts": {"00": 512, "11": 512}
        }

Step 10 app.js receives response:
        - Parses JSON
        - Extracts counts object
        - Calls Chart.js to render bar chart
        - Chart appears in browser
```

---

## API Specification

### Base URL
```
http://localhost:5000/api
```

All responses are JSON. All request bodies (where applicable) are JSON.

---

### GET /api/circuits

Returns all available quantum circuits.

**Request:** No parameters, no body.

**Response 200:**
```json
{
  "circuits": [
    {
      "id": "bell",
      "name": "Bell State",
      "description": "Creates a maximally entangled 2-qubit state.",
      "num_qubits": 2,
      "difficulty": "beginner"
    },
    {
      "id": "ghz",
      "name": "GHZ State",
      "description": "3-qubit generalized entangled state.",
      "num_qubits": 3,
      "difficulty": "beginner"
    },
    {
      "id": "teleportation",
      "name": "Quantum Teleportation",
      "description": "Transfers quantum state using entanglement.",
      "num_qubits": 3,
      "difficulty": "intermediate"
    },
    {
      "id": "grover",
      "name": "Grover's Algorithm",
      "description": "Quantum search: finds marked state quadratically faster.",
      "num_qubits": 2,
      "difficulty": "intermediate"
    }
  ]
}
```

---

### POST /api/simulate

Runs a circuit simulation with specified noise level.

**Request body:**
```json
{
  "circuit": "bell",
  "error_rate": 0.05,
  "shots": 1024
}
```

| Field | Type | Required | Constraints |
|---|---|---|---|
| circuit | string | Yes | Must be one of: bell, ghz, teleportation, grover |
| error_rate | float | Yes | 0.0 ≤ error_rate ≤ 0.20 |
| shots | integer | No | 100 ≤ shots ≤ 8192 (default: 1024) |

**Response 200:**
```json
{
  "simulation_id": 42,
  "circuit": "bell",
  "error_rate": 0.05,
  "shots": 1024,
  "counts": {
    "00": 467,
    "01": 28,
    "10": 22,
    "11": 507
  },
  "ideal_counts": {
    "00": 512,
    "11": 512
  },
  "created_at": "2024-01-15T14:32:00"
}
```

**Response 400** — missing or invalid field:
```json
{"error": "circuit is required", "code": "MISSING_FIELD"}
```

**Response 422** — out of range:
```json
{"error": "error_rate must be between 0.0 and 0.20", "code": "OUT_OF_RANGE"}
```

**Response 500** — simulation crashed:
```json
{"error": "Simulation failed. See server logs.", "code": "SIMULATION_ERROR"}
```

---

### GET /api/results/\<id\>

Retrieves a past simulation by its ID.

**URL parameter:** `id` — integer

**Response 200:**
```json
{
  "simulation": {
    "id": 42,
    "circuit": "bell",
    "error_rate": 0.05,
    "shots": 1024,
    "created_at": "2024-01-15T14:32:00"
  },
  "results": [
    {"state": "00", "count": 467},
    {"state": "01", "count": 28},
    {"state": "10", "count": 22},
    {"state": "11", "count": 507}
  ]
}
```

**Response 404** — ID not found:
```json
{"error": "Simulation 42 not found", "code": "NOT_FOUND"}
```

---

### GET /api/history

Returns last N simulations (for the history panel).

**Query parameters:**
- `limit` (optional, default 20): max results to return
- `circuit` (optional): filter by circuit name

**Response 200:**
```json
{
  "simulations": [
    {
      "id": 42,
      "circuit": "bell",
      "error_rate": 0.05,
      "shots": 1024,
      "created_at": "2024-01-15T14:32:00"
    }
  ],
  "total": 1
}
```

---

## Database Schema

### Tables

```sql
-- Circuit definitions (seeded on startup, never changes)
CREATE TABLE circuits (
    id          TEXT PRIMARY KEY,          -- 'bell', 'ghz', 'teleportation', 'grover'
    name        TEXT NOT NULL,             -- Display name: 'Bell State'
    description TEXT,                      -- Shown in UI tooltip
    num_qubits  INTEGER NOT NULL,          -- 2 or 3
    difficulty  TEXT DEFAULT 'beginner'    -- 'beginner' or 'intermediate'
);

-- One row per simulation run
CREATE TABLE simulations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    circuit_id  TEXT NOT NULL,
    error_rate  REAL NOT NULL,             -- 0.0 to 0.20
    shots       INTEGER NOT NULL,          -- 100 to 8192
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (circuit_id) REFERENCES circuits(id)
);

-- One row per unique measurement outcome per simulation
CREATE TABLE results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    simulation_id INTEGER NOT NULL,
    state         TEXT NOT NULL,           -- '00', '01', '10', '11', '000', etc.
    count         INTEGER NOT NULL,        -- How many times this state appeared
    FOREIGN KEY (simulation_id) REFERENCES simulations(id) ON DELETE CASCADE
);
```

### Entity Relationship Diagram

```
circuits                simulations              results
────────                ───────────              ───────
id (PK) ◄────────────  circuit_id (FK)   ┌──── simulation_id (FK)
name                    id (PK) ◄─────────┘     id (PK)
description             error_rate               state
num_qubits              shots                    count
difficulty              created_at
```

---

## File Structure

```
quantum-dashboard/
│
├── backend/
│   ├── quantum_engine.py     # Circuit definitions + Qiskit simulation runner
│   │                         # Functions: build_bell(), build_ghz(),
│   │                         #            build_teleportation(), build_grover(),
│   │                         #            run_circuit(name, error_rate, shots)
│   │
│   ├── noise_models.py       # Noise model factory
│   │                         # Functions: build_noise_model(error_rate)
│   │                         #            get_ideal_counts(circuit_name)
│   │
│   ├── database.py           # SQLite CRUD operations
│   │                         # Functions: init_db(), save_simulation(),
│   │                         #            get_simulation(), get_history()
│   │
│   └── app.py                # Flask application entry point
│                             # Routes: /api/circuits, /api/simulate,
│                             #         /api/results/<id>, /api/history
│
├── frontend/
│   ├── index.html            # Single-page application shell
│   └── static/
│       ├── js/
│       │   └── app.js        # All frontend logic:
│       │                     # - Event listeners (button clicks, slider)
│       │                     # - fetch() calls to Flask API
│       │                     # - DOM updates (show/hide panels)
│       │                     # - Chart.js configuration and rendering
│       └── css/
│           └── styles.css    # All visual styling
│
├── tests/
│   ├── test_quantum_engine.py  # Unit tests for circuit outputs
│   └── test_api.py             # Integration tests for Flask routes
│
├── data/
│   └── quantum_circuits.db     # SQLite file (auto-created, git-ignored)
│
└── docs/                       # You are here
```
