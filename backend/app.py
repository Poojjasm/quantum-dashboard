"""
app.py — Flask REST API
========================

This is the entry point for the entire backend. It:
  1. Creates the Flask application
  2. Enables CORS so the browser can call our API
  3. Initialises the database (creates tables if they don't exist)
  4. Defines four API routes that the frontend calls
  5. Serves the frontend HTML/JS/CSS as static files

ARCHITECTURE POSITION:
  Browser → HTTP/JSON → app.py (YOU ARE HERE) → quantum_engine.py
                                              → noise_models.py
                                              → database.py

HOW TO RUN:
  source venv/bin/activate
  python backend/app.py
  # Server starts at http://localhost:5001

HOW TO TEST (in a second terminal):
  curl http://localhost:5001/api/circuits
  curl -X POST http://localhost:5001/api/simulate \
       -H "Content-Type: application/json" \
       -d '{"circuit":"bell","error_rate":0.05}'
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()  # loads .env file in dev; env vars set directly in Railway for prod

# ── Make sure Python can find our other backend modules ──────────────────────
# When running `python backend/app.py`, Python adds backend/ to sys.path.
# But when Flask's dev server restarts itself on file changes, it may run from
# the project root. This insert ensures imports work in both cases.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS

from quantum_engine import run_named_circuit, get_ideal_counts, CIRCUIT_BUILDERS
from noise_models import describe_noise
from database import init_db, save_simulation, get_simulation, get_history, get_all_circuits

# ─────────────────────────────────────────────────────────────────────────────
# APP SETUP
# ─────────────────────────────────────────────────────────────────────────────

# Tell Flask where the frontend static files live.
# static_folder: directory to serve files from
# static_url_path: URL prefix for static files ("" = serve from root)
_HERE = os.path.dirname(os.path.abspath(__file__))
_FRONTEND = os.path.join(_HERE, "..", "frontend")

app = Flask(
    __name__,
    static_folder=os.path.join(_FRONTEND, "static"),
    static_url_path="/static",
)

# CORS: restrict to allowed origins in production.
# ALLOWED_ORIGINS env var = your Vercel URL, set in Railway dashboard.
# Falls back to "*" in development (no env var set).
_raw_origins = os.environ.get("ALLOWED_ORIGINS", "*")
_origins = [o.strip() for o in _raw_origins.split(",")] if _raw_origins != "*" else "*"
CORS(app, origins=_origins)

# Initialise database on startup — creates tables + seeds circuits if needed.
# Safe to call every time: CREATE TABLE IF NOT EXISTS, INSERT OR IGNORE.
init_db()

# The set of valid circuit names — derived from CIRCUIT_BUILDERS dict in
# quantum_engine.py so there's one source of truth.
VALID_CIRCUITS = set(CIRCUIT_BUILDERS.keys())


# ─────────────────────────────────────────────────────────────────────────────
# FRONTEND SERVING
# Flask serves index.html for the root URL so you only need one server running.
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    """Serve the frontend single-page application."""
    return send_from_directory(_FRONTEND, "index.html")


# ─────────────────────────────────────────────────────────────────────────────
# API ROUTES
# ─────────────────────────────────────────────────────────────────────────────

@app.route("/api/circuits", methods=["GET"])
def api_circuits():
    """
    GET /api/circuits
    -----------------
    Returns the list of all 4 available quantum circuits.

    The frontend uses this to populate the circuit selector dropdown on page load.
    Data comes from the circuits table in SQLite (seeded in init_db()).

    Response 200:
        {
            "circuits": [
                {"id": "bell", "name": "Bell State", "num_qubits": 2, ...},
                ...
            ]
        }
    """
    circuits = get_all_circuits()
    return jsonify({"circuits": circuits})


@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    """
    POST /api/simulate
    ------------------
    Run a quantum circuit simulation and return the results.

    This is the core endpoint — it:
      1. Validates the request body
      2. Calls quantum_engine.run_named_circuit() to run the Qiskit simulation
      3. Saves the result to SQLite via database.save_simulation()
      4. Returns the counts + ideal reference counts as JSON

    Request body (JSON):
        {
            "circuit":    "bell",   required  — one of: bell, ghz, teleportation, grover
            "error_rate": 0.05,     required  — float 0.0 – 0.20
            "shots":      1024      optional  — int 100–8192, default 1024
        }

    Response 200:
        {
            "simulation_id":   42,
            "circuit":         "bell",
            "circuit_name":    "Bell State",
            "error_rate":      0.05,
            "shots":           1024,
            "counts":          {"00": 467, "01": 26, "10": 19, "11": 512},
            "ideal_counts":    {"00": 512, "11": 512},
            "noise_label":     "Moderate noise — errors are visible...",
            "created_at":      "2024-01-15 14:32:00"
        }
    """
    # ── Parse request body ────────────────────────────────────────────────────
    # request.get_json() parses the JSON body.
    # silent=True returns None instead of raising an exception on bad JSON.
    body = request.get_json(silent=True)

    if not body or not isinstance(body, dict):
        return _error("Request body must be valid JSON.", "BAD_REQUEST", 400)

    # ── Validate: circuit ─────────────────────────────────────────────────────
    circuit_name = body.get("circuit")
    if not circuit_name:
        return _error("'circuit' is required.", "MISSING_FIELD", 400)
    if not isinstance(circuit_name, str):
        return _error("'circuit' must be a string.", "WRONG_TYPE", 400)
    if circuit_name not in VALID_CIRCUITS:
        return _error(
            f"Invalid circuit '{circuit_name}'. "
            f"Choose from: {sorted(VALID_CIRCUITS)}",
            "INVALID_CIRCUIT",
            400,
        )

    # ── Validate: error_rate ──────────────────────────────────────────────────
    raw_rate = body.get("error_rate")
    if raw_rate is None:
        return _error("'error_rate' is required.", "MISSING_FIELD", 400)
    try:
        error_rate = float(raw_rate)
    except (TypeError, ValueError):
        return _error("'error_rate' must be a number.", "WRONG_TYPE", 400)
    if not (0.0 <= error_rate <= 0.20):
        return _error(
            "'error_rate' must be between 0.0 and 0.20.",
            "OUT_OF_RANGE",
            422,
        )

    # ── Validate: shots (optional) ────────────────────────────────────────────
    raw_shots = body.get("shots", 1024)
    try:
        shots = int(raw_shots)
    except (TypeError, ValueError):
        return _error("'shots' must be an integer.", "WRONG_TYPE", 400)
    # Clamp to valid range rather than erroring — friendlier UX
    shots = max(100, min(8192, shots))

    # ── Run simulation ────────────────────────────────────────────────────────
    # This calls quantum_engine.py → noise_models.py → Qiskit AerSimulator.
    # It's the most expensive step (30ms–2s depending on circuit + shots).
    try:
        counts = run_named_circuit(circuit_name, error_rate, shots)
    except Exception as exc:
        # Log to server console for debugging, return generic error to client.
        app.logger.error("Simulation error: %s", exc, exc_info=True)
        return _error(f"Simulation failed: {exc}", "SIMULATION_ERROR", 500)

    # ── Persist to database ───────────────────────────────────────────────────
    try:
        simulation_id = save_simulation(circuit_name, error_rate, shots, counts)
    except Exception as exc:
        app.logger.error("Database error: %s", exc, exc_info=True)
        return _error("Failed to save simulation results.", "DB_ERROR", 500)

    # ── Build response ────────────────────────────────────────────────────────
    ideal = get_ideal_counts(circuit_name, shots)

    # Get the circuit display name from the DB (e.g. "Bell State" for "bell")
    all_circuits = {c["id"]: c["name"] for c in get_all_circuits()}
    circuit_display_name = all_circuits.get(circuit_name, circuit_name)

    return jsonify({
        "simulation_id":  simulation_id,
        "circuit":        circuit_name,
        "circuit_name":   circuit_display_name,
        "error_rate":     error_rate,
        "shots":          shots,
        "counts":         counts,
        "ideal_counts":   ideal,
        "noise_label":    describe_noise(error_rate),
    })


@app.route("/api/results/<int:simulation_id>", methods=["GET"])
def api_results(simulation_id: int):
    """
    GET /api/results/<id>
    ----------------------
    Retrieve a past simulation by its integer ID.

    The <int:simulation_id> in the route means Flask automatically:
      - Extracts the integer from the URL  (/api/results/42 → 42)
      - Returns 404 if it's not a valid integer (/api/results/abc → 404)

    Response 200:
        {
            "simulation": {id, circuit_id, circuit_name, error_rate, shots, created_at},
            "results":    [{"state": "00", "count": 467}, ...]
        }

    Response 404:
        {"error": "Simulation 42 not found.", "code": "NOT_FOUND"}
    """
    data = get_simulation(simulation_id)

    if data is None:
        return _error(f"Simulation {simulation_id} not found.", "NOT_FOUND", 404)

    return jsonify(data)


@app.route("/api/history", methods=["GET"])
def api_history():
    """
    GET /api/history
    ----------------
    Return recent simulations, newest first.

    Used by the frontend history panel to show past runs.
    Supports optional query parameters:
      ?limit=10        — return at most 10 simulations (default: 20)
      ?circuit=bell    — filter to only Bell State simulations

    Response 200:
        {
            "simulations": [{id, circuit_name, error_rate, shots, created_at}, ...],
            "total": 3
        }
    """
    # request.args is a dict of query parameters from the URL
    # e.g. /api/history?limit=5&circuit=bell → {"limit": "5", "circuit": "bell"}
    limit = request.args.get("limit", 20, type=int)
    limit = max(1, min(100, limit))   # clamp: 1–100

    circuit_filter = request.args.get("circuit")
    if circuit_filter and circuit_filter not in VALID_CIRCUITS:
        return _error(
            f"Invalid circuit filter '{circuit_filter}'.",
            "INVALID_CIRCUIT",
            400,
        )

    simulations = get_history(limit=limit, circuit_filter=circuit_filter)
    return jsonify({"simulations": simulations, "total": len(simulations)})


# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL ERROR HANDLERS
# These catch errors that slip through the route handlers.
# Flask calls these automatically for 404 / 500 errors.
# ─────────────────────────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    """Return JSON 404 instead of Flask's default HTML error page."""
    return _error("The requested URL was not found.", "NOT_FOUND", 404)


@app.errorhandler(405)
def method_not_allowed(e):
    """Return JSON 405 for wrong HTTP method (e.g. GET on /api/simulate)."""
    return _error("Method not allowed on this endpoint.", "METHOD_NOT_ALLOWED", 405)


@app.errorhandler(500)
def internal_error(e):
    """Return JSON 500 instead of Flask's default HTML error page."""
    return _error("An unexpected server error occurred.", "INTERNAL_ERROR", 500)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _error(message: str, code: str, status: int):
    """
    Return a consistent JSON error response.

    Every error in this API has the same shape:
        {"error": "Human-readable message.", "code": "MACHINE_CODE"}

    The "code" field lets the frontend switch on specific errors programmatically
    without parsing the human message string (which might change).

    Args:
        message: Human-readable description (shown to developers in logs/tools)
        code:    Machine-readable error code (used in frontend logic)
        status:  HTTP status code (400, 404, 422, 500, etc.)
    """
    return jsonify({"error": message, "code": code}), status


# ─────────────────────────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("=" * 55)
    print(" Quantum Dashboard — Flask API")
    print("=" * 55)
    print(f" API:      http://localhost:5001/api/circuits")
    print(f" Frontend: http://localhost:5001/")
    print(f" Database: {os.path.relpath(os.path.join(_HERE, '..', 'data', 'quantum_circuits.db'))}")
    print("=" * 55)
    print(" Press CTRL+C to stop\n")

    # debug=True:
    #   - Auto-reloads when you save a Python file (huge dev time saver)
    #   - Shows detailed tracebacks in the browser on errors
    #   - NEVER use in production (exposes internals)
    # NOTE: macOS reserves port 5000 for AirPlay Receiver.
    # We use 5001 to avoid that conflict.
    app.run(debug=True, port=5001)
