# Database Schema — Quantum Circuit Error Analyzer

## Why SQLite?

For this project we use **SQLite** — a file-based database that requires zero server setup.
The entire database lives in a single file (`data/quantum_circuits.db`).

| Feature | SQLite | PostgreSQL / MySQL |
|---|---|---|
| Setup | None — just a file | Requires installing a server |
| Good for | Learning, small projects, local dev | Production, large scale, concurrent users |
| Limitation | Not great for many simultaneous writers | Handles high concurrency |
| Use it when | 1 user, 1 app, learning SQL | Multiple servers, high traffic |

**Real talk:** For this 2-week project, SQLite is 100% the right choice.
When you grow this into a production app, migrating to PostgreSQL is straightforward.

---

## Entity Relationship Diagram

```
┌──────────────────────┐       ┌─────────────────────────────┐
│       circuits        │       │         simulations          │
├──────────────────────┤       ├─────────────────────────────┤
│ id (TEXT, PK)        │──────▶│ id (INTEGER, PK, AUTOINCR.) │
│ name (TEXT)          │ 1   N │ circuit_id (TEXT, FK)        │
│ description (TEXT)   │       │ error_rate (REAL)            │
│ num_qubits (INTEGER) │       │ shots (INTEGER)              │
│ difficulty (TEXT)    │       │ created_at (DATETIME)        │
└──────────────────────┘       └──────────────┬──────────────┘
                                               │
                                               │ 1
                                               │
                                               ▼ N
                               ┌─────────────────────────────┐
                               │           results            │
                               ├─────────────────────────────┤
                               │ id (INTEGER, PK, AUTOINCR.) │
                               │ simulation_id (INTEGER, FK)  │
                               │ state (TEXT)                 │
                               │ count (INTEGER)              │
                               └─────────────────────────────┘
```

**Relationships:**
- One **circuit** can have many **simulations** (you run the same circuit many times)
- One **simulation** can have many **results** (one row per unique measurement outcome)

---

## Table Definitions

### Table: `circuits`

Stores the 4 quantum circuit definitions. This data is seeded once at startup and never changes.

```sql
CREATE TABLE IF NOT EXISTS circuits (
    id          TEXT PRIMARY KEY,
    -- 'bell', 'ghz', 'teleportation', 'grover'
    -- TEXT because it's a readable slug, not a number

    name        TEXT NOT NULL,
    -- 'Bell State', 'GHZ State', etc.
    -- NOT NULL means this column is required

    description TEXT,
    -- Longer explanation shown in the UI
    -- No NOT NULL = NULL is allowed (optional)

    num_qubits  INTEGER NOT NULL,
    -- 2 or 3 — how many qubits this circuit uses

    difficulty  TEXT DEFAULT 'beginner'
    -- 'beginner' or 'intermediate'
    -- DEFAULT means if not specified, use 'beginner'
);
```

**Seed data (inserted once at startup):**

```sql
INSERT OR IGNORE INTO circuits VALUES
    ('bell',          'Bell State',            'Creates a maximally entangled 2-qubit state.', 2, 'beginner'),
    ('ghz',           'GHZ State',             '3-qubit generalized entangled state.',          3, 'beginner'),
    ('teleportation', 'Quantum Teleportation', 'Transfers quantum state using entanglement.',   3, 'intermediate'),
    ('grover',        'Grover''s Algorithm',   'Quantum search: finds marked state quadratically faster.', 2, 'intermediate');
```

*Note: `INSERT OR IGNORE` — if the row already exists (same PK), skip it. Safe to re-run.*

---

### Table: `simulations`

One row per simulation run. Records what was run and when.

```sql
CREATE TABLE IF NOT EXISTS simulations (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Auto-incrementing integer ID
    -- Every new row gets the next number: 1, 2, 3, ...

    circuit_id  TEXT NOT NULL,
    -- Which circuit was run — references circuits.id
    -- NOT NULL: every simulation must have a circuit

    error_rate  REAL NOT NULL,
    -- The depolarizing error rate used: 0.0 to 0.20
    -- REAL = floating point number in SQLite

    shots       INTEGER NOT NULL,
    -- Number of simulation runs: 100 to 8192
    -- More shots = more accurate statistics

    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    -- Auto-filled with the current date/time when inserted
    -- Format: '2024-01-15 14:32:00'

    FOREIGN KEY (circuit_id) REFERENCES circuits(id)
    -- Enforces that circuit_id must exist in the circuits table
    -- Prevents orphaned simulation records
);
```

---

### Table: `results`

One row per unique measurement outcome per simulation.

```sql
CREATE TABLE IF NOT EXISTS results (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    -- Auto-incrementing ID

    simulation_id INTEGER NOT NULL,
    -- References simulations.id — which run produced this result

    state         TEXT NOT NULL,
    -- The measurement outcome as a binary string
    -- Examples: '00', '01', '10', '11' (2-qubit)
    --           '000', '001', ..., '111' (3-qubit)

    count         INTEGER NOT NULL,
    -- How many times this state appeared out of total shots
    -- All counts for a simulation_id should sum to shots

    FOREIGN KEY (simulation_id) REFERENCES simulations(id)
        ON DELETE CASCADE
    -- If you delete a simulation, all its results are deleted too
    -- This prevents "orphaned" result rows with no parent
);
```

---

## Sample Data

After running a Bell State simulation with `error_rate=0.05, shots=1024`:

**circuits table:**
| id | name | description | num_qubits | difficulty |
|---|---|---|---|---|
| bell | Bell State | Creates a maximally entangled... | 2 | beginner |
| ghz | GHZ State | 3-qubit generalized... | 3 | beginner |
| teleportation | Quantum Teleportation | Transfers quantum state... | 3 | intermediate |
| grover | Grover's Algorithm | Quantum search... | 2 | intermediate |

**simulations table:**
| id | circuit_id | error_rate | shots | created_at |
|---|---|---|---|---|
| 1 | bell | 0.05 | 1024 | 2024-01-15 14:32:00 |

**results table:**
| id | simulation_id | state | count |
|---|---|---|---|
| 1 | 1 | 00 | 467 |
| 2 | 1 | 01 | 28 |
| 3 | 1 | 10 | 22 |
| 4 | 1 | 11 | 507 |

*Sum of counts: 467 + 28 + 22 + 507 = 1024 ✓ (matches shots)*

---

## Common Queries

### Get a simulation with its results

```sql
-- Fetch simulation metadata
SELECT s.id, c.name AS circuit_name, s.error_rate, s.shots, s.created_at
FROM simulations s
JOIN circuits c ON s.circuit_id = c.id
WHERE s.id = 1;

-- Fetch its results
SELECT state, count
FROM results
WHERE simulation_id = 1
ORDER BY state;
```

### Get simulation history (most recent first)

```sql
SELECT s.id, c.name AS circuit_name, s.error_rate, s.shots, s.created_at
FROM simulations s
JOIN circuits c ON s.circuit_id = c.id
ORDER BY s.created_at DESC
LIMIT 20;
```

### Count total simulations per circuit

```sql
SELECT c.name, COUNT(s.id) AS run_count
FROM circuits c
LEFT JOIN simulations s ON c.id = s.circuit_id
GROUP BY c.id
ORDER BY run_count DESC;
```

### Find most error-degraded simulations

```sql
-- Find simulations where noise caused the most unexpected states
-- (states not in the ideal distribution appear most)
SELECT s.id, c.name, s.error_rate,
       SUM(r.count) AS total_shots,
       COUNT(r.id) AS num_unique_states
FROM simulations s
JOIN circuits c ON s.circuit_id = c.id
JOIN results r ON s.id = r.simulation_id
GROUP BY s.id
ORDER BY num_unique_states DESC, s.error_rate DESC
LIMIT 10;
```

---

## Database Design Decisions

### Why separate `results` table instead of storing counts as JSON?

**Option A** (what we did):
```sql
results: simulation_id=1, state='00', count=467
results: simulation_id=1, state='01', count=28
```

**Option B** (alternative):
```sql
simulations: counts='{"00": 467, "01": 28}' (JSON string in one column)
```

**We chose Option A because:**
- You can query individual states: `WHERE state = '11'`
- You can aggregate across simulations: `AVG(count) WHERE state = '00'`
- Proper database normalization — each fact is stored once
- JSON in SQL columns is harder to query and index

---

## SQLite Type Affinity (Quick Reference)

SQLite is loosely typed — column types are suggestions, not hard rules:

| SQLite Type | Stores | Python equivalent |
|---|---|---|
| `INTEGER` | Whole numbers | `int` |
| `REAL` | Decimal numbers | `float` |
| `TEXT` | Strings | `str` |
| `BLOB` | Binary data | `bytes` |
| `NULL` | No value | `None` |

`DATETIME` in SQLite is actually stored as `TEXT` in ISO 8601 format (`'2024-01-15 14:32:00'`).
Python's `sqlite3` module converts it automatically.
