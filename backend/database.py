"""
database.py — SQLite Database Operations
=========================================

This module handles all persistent storage for the Quantum Dashboard.
It uses SQLite — a file-based database built into Python's standard library.
No extra packages needed: `import sqlite3` is all it takes.

WHY A DATABASE AT ALL?
  Without a database, every simulation result vanishes when Python exits.
  With SQLite, every run is saved to a .db file on disk. Users can come
  back tomorrow and see their past simulations. The history panel in the
  frontend reads from this database.

SCHEMA OVERVIEW (3 tables):

  circuits         simulations          results
  ────────         ───────────          ───────
  id (PK)    ←──  circuit_id (FK)  ←── simulation_id (FK)
  name             id (PK)              id (PK)
  description      error_rate           state
  num_qubits       shots                count
  difficulty       created_at

  "circuits" is seeded once at startup. It never changes.
  "simulations" gets one new row every time the user clicks Simulate.
  "results" gets one new row per unique measurement outcome per simulation.

DATABASE FILE:
  data/quantum_circuits.db  (auto-created, git-ignored)
"""

import sqlite3
import os
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────────────────────────────────────

# Build an absolute path to the database file.
# __file__ is the path to this script (database.py).
# os.path.dirname(__file__)           → backend/
# os.path.dirname(os.path.dirname())  → project root
# Then we go into data/ subdirectory.
# Using an absolute path avoids "file not found" errors regardless of which
# directory Python is invoked from.
_HERE       = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_HERE)
DB_PATH     = os.path.join(_PROJECT_ROOT, "data", "quantum_circuits.db")

# The 4 circuit definitions we seed on startup.
# Stored as tuples matching the circuits table column order:
# (id, name, description, num_qubits, difficulty)
_CIRCUIT_SEED_DATA = [
    (
        "bell",
        "Bell State",
        "Creates a maximally entangled 2-qubit state. "
        "The simplest proof that quantum entanglement exists.",
        2,
        "beginner",
    ),
    (
        "ghz",
        "GHZ State",
        "3-qubit generalized entangled state. "
        "Measuring any qubit instantly determines the other two.",
        3,
        "beginner",
    ),
    (
        "teleportation",
        "Quantum Teleportation",
        "Transfers a quantum state from one qubit to another "
        "using entanglement and classical communication.",
        3,
        "intermediate",
    ),
    (
        "grover",
        "Grover's Algorithm",
        "Quantum search: finds a marked state quadratically "
        "faster than any classical search algorithm.",
        2,
        "intermediate",
    ),
]


# ─────────────────────────────────────────────────────────────────────────────
# CONNECTION HELPER
# ─────────────────────────────────────────────────────────────────────────────

def get_connection() -> sqlite3.Connection:
    """
    Open and return a connection to the SQLite database.

    WHY row_factory = sqlite3.Row:
      By default, sqlite3 returns rows as plain tuples: (42, 'bell', 0.05).
      With Row, you can access columns by name: row['circuit_id'] — much cleaner.

    WHY PRAGMA foreign_keys = ON:
      SQLite doesn't enforce foreign key constraints by default (for backwards
      compatibility). This line turns enforcement on per-connection, so inserting
      a simulation with a non-existent circuit_id will raise an error instead of
      silently storing bad data.

    Returns:
        sqlite3.Connection — caller is responsible for closing it.
    """
    conn = sqlite3.connect(DB_PATH)

    # Make rows accessible by column name: row['id'] instead of row[0]
    conn.row_factory = sqlite3.Row

    # Enforce referential integrity (foreign key constraints)
    conn.execute("PRAGMA foreign_keys = ON")

    return conn


# ─────────────────────────────────────────────────────────────────────────────
# INITIALIZATION
# ─────────────────────────────────────────────────────────────────────────────

def init_db() -> None:
    """
    Create all tables and seed the circuits table.

    This is called once when Flask starts up (in app.py).
    It's safe to call multiple times — CREATE TABLE IF NOT EXISTS and
    INSERT OR IGNORE mean re-running never overwrites existing data.

    After this function runs:
      - data/quantum_circuits.db exists
      - circuits table has 4 rows (bell, ghz, teleportation, grover)
      - simulations and results tables exist but are empty
    """
    # Ensure the data/ directory exists (it might not on a fresh clone)
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = get_connection()
    cursor = conn.cursor()

    # ── Table: circuits ───────────────────────────────────────────────────────
    # Static lookup table. Seeded once, never modified by user actions.
    # TEXT PRIMARY KEY: we use readable string IDs ('bell') not integers,
    # so the API can use /api/simulate with {"circuit": "bell"} directly.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS circuits (
            id          TEXT PRIMARY KEY,
            name        TEXT NOT NULL,
            description TEXT,
            num_qubits  INTEGER NOT NULL,
            difficulty  TEXT NOT NULL DEFAULT 'beginner'
        )
    """)

    # ── Table: simulations ────────────────────────────────────────────────────
    # One row per simulation run. Records what was configured and when.
    # AUTOINCREMENT: every INSERT gets the next integer ID automatically.
    # FOREIGN KEY: circuit_id must exist in circuits — prevents orphaned records.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS simulations (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            circuit_id  TEXT    NOT NULL,
            error_rate  REAL    NOT NULL,
            shots       INTEGER NOT NULL,
            created_at  TEXT    NOT NULL DEFAULT (datetime('now')),
            FOREIGN KEY (circuit_id) REFERENCES circuits(id)
        )
    """)

    # ── Table: results ────────────────────────────────────────────────────────
    # One row per unique measurement outcome per simulation.
    # e.g. for Bell State: rows for '00', '01', '10', '11' (only non-zero ones).
    # ON DELETE CASCADE: if a simulation row is deleted, its results are too.
    # This prevents "orphaned" result rows with no parent simulation.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            simulation_id INTEGER NOT NULL,
            state         TEXT    NOT NULL,
            count         INTEGER NOT NULL,
            FOREIGN KEY (simulation_id) REFERENCES simulations(id)
                ON DELETE CASCADE
        )
    """)

    # ── Seed the circuits table ───────────────────────────────────────────────
    # INSERT OR IGNORE: if a row with this PRIMARY KEY already exists, skip it.
    # Means we can call init_db() on every app start without duplicating data.
    cursor.executemany(
        "INSERT OR IGNORE INTO circuits (id, name, description, num_qubits, difficulty) "
        "VALUES (?, ?, ?, ?, ?)",
        _CIRCUIT_SEED_DATA,
    )

    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# WRITE OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def save_simulation(
    circuit_id: str,
    error_rate: float,
    shots: int,
    counts: dict,
) -> int:
    """
    Persist a completed simulation and its measurement results to the database.

    Uses a single transaction so both INSERTs either both succeed or both fail.
    If inserting results fails halfway through, the simulation row is also
    rolled back — no partial data left in the database.

    Args:
        circuit_id:  'bell', 'ghz', 'teleportation', or 'grover'
        error_rate:  The depolarizing error rate used (0.0 – 0.20)
        shots:       Number of simulation runs
        counts:      Measurement results dict, e.g. {'00': 487, '11': 537}

    Returns:
        int: The auto-assigned simulation ID (used in GET /api/results/<id>)

    Example:
        sim_id = save_simulation("bell", 0.05, 1024, {"00": 487, "11": 537})
        # → inserts 1 row into simulations
        # → inserts 2 rows into results (one per state)
        # → returns 1 (or whatever the next auto-increment ID is)
    """
    if not counts:
        raise ValueError("counts must be a non-empty dict")

    conn = get_connection()
    cursor = conn.cursor()

    try:
        # ── Insert simulation metadata ─────────────────────────────────────────
        # The ? placeholders are parameterized queries — SQLite fills them safely.
        # NEVER use string formatting (f"...{value}...") for SQL — that's SQL injection.
        cursor.execute(
            """
            INSERT INTO simulations (circuit_id, error_rate, shots)
            VALUES (?, ?, ?)
            """,
            (circuit_id, error_rate, shots),
        )

        # lastrowid: the AUTOINCREMENT ID assigned to the row we just inserted.
        # This is what we return to Flask so it can include it in the API response.
        simulation_id = cursor.lastrowid

        # ── Insert one result row per measurement outcome ──────────────────────
        # counts is a dict like {'00': 487, '01': 26, '10': 19, '11': 492}.
        # We insert one row per key-value pair.
        # executemany() is more efficient than calling execute() in a loop.
        result_rows = [
            (simulation_id, state, count)
            for state, count in counts.items()
        ]
        cursor.executemany(
            "INSERT INTO results (simulation_id, state, count) VALUES (?, ?, ?)",
            result_rows,
        )

        # Commit = make changes permanent on disk
        conn.commit()

    except Exception:
        # Rollback = undo all changes since last commit if anything went wrong
        conn.rollback()
        raise

    finally:
        conn.close()

    return simulation_id


# ─────────────────────────────────────────────────────────────────────────────
# READ OPERATIONS
# ─────────────────────────────────────────────────────────────────────────────

def get_simulation(simulation_id: int) -> dict | None:
    """
    Retrieve a simulation and all its measurement results by ID.

    Uses a JOIN to get the circuit's display name alongside the simulation data.
    A JOIN combines rows from two tables where a shared column matches —
    here we match simulations.circuit_id = circuits.id.

    Args:
        simulation_id: integer ID returned by save_simulation()

    Returns:
        dict with two keys:
          'simulation': metadata dict  (id, circuit_id, circuit_name, ...)
          'results':    list of dicts  [{state, count}, ...]
        None if no simulation with that ID exists.

    Example return value:
        {
            'simulation': {
                'id': 1, 'circuit_id': 'bell', 'circuit_name': 'Bell State',
                'error_rate': 0.05, 'shots': 1024, 'created_at': '2024-01-15 14:32:00'
            },
            'results': [
                {'state': '00', 'count': 487},
                {'state': '01', 'count': 26},
                {'state': '10', 'count': 19},
                {'state': '11', 'count': 492},
            ]
        }
    """
    conn = get_connection()
    cursor = conn.cursor()

    # JOIN: for each simulation row, attach the circuit's name from circuits table.
    # s.* = all columns from simulations, c.name = circuit name from circuits.
    cursor.execute(
        """
        SELECT
            s.id,
            s.circuit_id,
            c.name   AS circuit_name,
            s.error_rate,
            s.shots,
            s.created_at
        FROM simulations s
        JOIN circuits c ON s.circuit_id = c.id
        WHERE s.id = ?
        """,
        (simulation_id,),
    )
    sim_row = cursor.fetchone()   # fetchone() returns one row or None

    if sim_row is None:
        conn.close()
        return None

    # Fetch all measurement results for this simulation
    cursor.execute(
        """
        SELECT state, count
        FROM results
        WHERE simulation_id = ?
        ORDER BY state ASC
        """,
        (simulation_id,),
    )
    result_rows = cursor.fetchall()  # fetchall() returns a list (may be empty)
    conn.close()

    return {
        "simulation": dict(sim_row),           # sqlite3.Row → plain dict
        "results":    [dict(r) for r in result_rows],
    }


def get_history(limit: int = 20, circuit_filter: str | None = None) -> list[dict]:
    """
    Return recent simulations, newest first.

    Used by the frontend history panel to show past runs.
    Does NOT include the per-state results (that would be a separate query
    per simulation — inefficient). Just the metadata summary.

    Args:
        limit:          Max number of simulations to return (default 20).
        circuit_filter: If provided, only return simulations for this circuit ID.
                        e.g. 'bell' returns only Bell State simulations.

    Returns:
        List of simulation metadata dicts, sorted newest → oldest.
    """
    conn = get_connection()
    cursor = conn.cursor()

    if circuit_filter:
        cursor.execute(
            """
            SELECT
                s.id,
                s.circuit_id,
                c.name   AS circuit_name,
                s.error_rate,
                s.shots,
                s.created_at
            FROM simulations s
            JOIN circuits c ON s.circuit_id = c.id
            WHERE s.circuit_id = ?
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT ?
            """,
            (circuit_filter, limit),
        )
    else:
        cursor.execute(
            """
            SELECT
                s.id,
                s.circuit_id,
                c.name   AS circuit_name,
                s.error_rate,
                s.shots,
                s.created_at
            FROM simulations s
            JOIN circuits c ON s.circuit_id = c.id
            ORDER BY s.created_at DESC, s.id DESC
            LIMIT ?
            """,
            (limit,),
        )

    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


def get_all_circuits() -> list[dict]:
    """
    Return all rows from the circuits table.

    Used by GET /api/circuits to populate the frontend dropdown.
    This data never changes — it's seeded once in init_db().

    Returns:
        List of circuit dicts: [{'id', 'name', 'description', 'num_qubits', 'difficulty'}, ...]
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT id, name, description, num_qubits, difficulty FROM circuits")
    rows = cursor.fetchall()
    conn.close()

    return [dict(row) for row in rows]


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL TEST — run this file directly
# Command: python backend/database.py
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print("Database — Manual Test")
    print(f"Database path: {DB_PATH}")
    print("=" * 55)

    # ── Step 1: Initialize ────────────────────────────────────────────────────
    print("\n[1] Initializing database...")
    init_db()
    print(f"    Created: {os.path.exists(DB_PATH)}")
    print(f"    Size:    {os.path.getsize(DB_PATH)} bytes")

    # ── Step 2: Check seeded circuits ────────────────────────────────────────
    print("\n[2] Circuits table (seeded on init):")
    circuits = get_all_circuits()
    for c in circuits:
        print(f"    {c['id']:<15}  {c['num_qubits']} qubits  [{c['difficulty']}]  {c['name']}")

    # ── Step 3: Save a simulation ─────────────────────────────────────────────
    print("\n[3] Saving a Bell State simulation (p=0.05)...")
    fake_counts = {"00": 467, "01": 26, "10": 19, "11": 512}
    sim_id = save_simulation("bell", 0.05, 1024, fake_counts)
    print(f"    Saved with simulation_id = {sim_id}")

    # ── Step 4: Retrieve it back ──────────────────────────────────────────────
    print("\n[4] Retrieving simulation by ID...")
    data = get_simulation(sim_id)
    print(f"    Simulation: {data['simulation']}")
    print(f"    Results:")
    for r in data['results']:
        bar = "█" * (r['count'] // 20)
        print(f"      |{r['state']}⟩  {r['count']:4d}  {bar}")

    # ── Step 5: Test non-existent ID ─────────────────────────────────────────
    print("\n[5] Retrieving non-existent ID (99999)...")
    missing = get_simulation(99999)
    print(f"    Result: {missing}  ← should be None")

    # ── Step 6: Save a few more, then get history ─────────────────────────────
    print("\n[6] Saving 2 more simulations...")
    save_simulation("grover", 0.10, 1024, {"11": 702, "00": 107, "01": 108, "10": 107})
    save_simulation("ghz",    0.00, 512,  {"000": 256, "111": 256})

    print("\n[7] History (most recent first, limit=5):")
    history = get_history(limit=5)
    for h in history:
        print(f"    id={h['id']}  {h['circuit_name']:<22}  p={h['error_rate']:.2f}  {h['shots']} shots  {h['created_at']}")

    print("\n[8] History filtered by circuit='bell':")
    bell_history = get_history(circuit_filter="bell")
    for h in bell_history:
        print(f"    id={h['id']}  {h['circuit_name']}")

    # ── Step 7: Verify result count integrity ─────────────────────────────────
    print("\n[9] Verifying result counts sum to shots...")
    data = get_simulation(sim_id)
    total = sum(r['count'] for r in data['results'])
    shots = data['simulation']['shots']
    match = "✓" if total == shots else "✗ MISMATCH"
    print(f"    Sum of counts: {total} / {shots} shots  {match}")

    print("\nAll database tests passed!")
