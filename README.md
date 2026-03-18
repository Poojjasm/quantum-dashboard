# Quantum Circuit Error Analyzer Dashboard

> A full-stack web app that simulates quantum circuits under realistic noise conditions
> and visualizes how errors degrade quantum computation.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.1-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/React-18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![Qiskit](https://img.shields.io/badge/Qiskit-2.x-6929C4?style=flat&logo=qiskit)](https://qiskit.org/)
[![uv](https://img.shields.io/badge/uv-managed-DE5FE9?style=flat)](https://docs.astral.sh/uv/)
[![Tests](https://img.shields.io/badge/tests-89%20passing-4ade80?style=flat)](#testing)
[![Live Demo](https://img.shields.io/badge/Live%20Demo-Vercel-000000?style=flat&logo=vercel)](https://quantum-dashboard-jade.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Live:** [quantum-dashboard-jade.vercel.app](https://quantum-dashboard-jade.vercel.app)

---

## What This Project Does

Real quantum computers are powerful but **noisy**. Qubits lose their quantum properties
due to heat, vibrations, and electromagnetic interference — a process called **decoherence**.

This dashboard lets you explore that problem interactively:

1. **Pick a quantum circuit** — Bell State, GHZ State, Quantum Teleportation, or Grover's Algorithm
2. **Set an error rate** — from 0% (perfect, theoretical) to 20% (very noisy)
3. **Hit Simulate** — Qiskit runs the circuit with your noise level on the backend
4. **See the results** — bar chart compares your noisy result against the ideal
5. **Run a Noise Sweep** — plot how fidelity degrades across 8 error rates at once

---

## Features

- **4 Quantum Circuits** — Bell State, GHZ State, Quantum Teleportation, Grover's Algorithm
- **Adjustable Noise** — Depolarizing error model, 0–20% error rate with preset buttons
- **Live Visualization** — Chart.js bar charts comparing noisy vs ideal distributions
- **Noise Sweep** — Fidelity-vs-error-rate line chart across 8 data points with live progress
- **Simulation History** — All past runs saved to SQLite, displayed in the history panel
- **REST API** — Clean Flask endpoints for circuit selection, simulation, and history
- **Deployed** — Flask on Railway, React/Vite on Vercel with proxy rewrite

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Quantum Engine** | Qiskit 2.x + Qiskit Aer |
| **Backend API** | Flask 3.1 (Python 3.11) |
| **Database** | SQLite (built into Python) |
| **Frontend** | React 18 + Vite |
| **Visualization** | Chart.js via react-chartjs-2 |
| **Package Manager** | uv |
| **Backend Deploy** | Railway (Gunicorn) |
| **Frontend Deploy** | Vercel |

---

## Quick Start

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`
- Node.js 18+ (for frontend only)

### Backend

```bash
git clone https://github.com/Poojjasm/quantum-dashboard.git
cd quantum-dashboard

# Install dependencies and run
uv sync
uv run python backend/app.py
# → API running at http://localhost:5001
```

### Frontend (dev)

```bash
cd frontend
npm install
npm run dev
# → UI at http://localhost:5173
```

Or just visit the live deployment at [quantum-dashboard-jade.vercel.app](https://quantum-dashboard-jade.vercel.app).

---

## Testing

```bash
uv run pytest
# 89 tests across 4 test files — all passing
```

| Test File | What It Tests |
|---|---|
| `tests/test_quantum_engine.py` | Circuit builders, ideal counts, simulation output |
| `tests/test_noise_models.py` | Noise model construction, describe_noise labels |
| `tests/test_database.py` | SQLite CRUD — save, retrieve, history, filtering |
| `tests/test_api.py` | All Flask endpoints — validation, success paths, error handlers |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/circuits` | Returns all 4 available circuits |
| `POST` | `/api/simulate` | Runs a simulation with circuit + error rate |
| `GET` | `/api/results/<id>` | Retrieves a past simulation by ID |
| `GET` | `/api/history` | Returns recent simulations (supports `?limit` and `?circuit` filters) |

**Example:**
```bash
curl -X POST https://web-production-187b7.up.railway.app/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.05, "shots": 1024}'
```

See [docs/API_REFERENCE.md](docs/API_REFERENCE.md) for full documentation.

---

## Project Structure

```
quantum-dashboard/
├── backend/
│   ├── quantum_engine.py    # Qiskit circuit builders + AerSimulator runner
│   ├── noise_models.py      # Depolarizing noise model + noise labels
│   ├── database.py          # SQLite schema, CRUD operations
│   └── app.py               # Flask REST API (4 endpoints)
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── ControlsPanel.jsx
│   │   │   ├── ResultsPanel.jsx
│   │   │   ├── FidelityChart.jsx
│   │   │   └── HistoryPanel.jsx
│   │   └── hooks/
│   │       └── useSimulation.js
│   └── vercel.json
├── specs/
│   ├── 001-quantum-engine/spec.md
│   ├── 002-noise-models/spec.md
│   ├── 003-flask-api/spec.md
│   └── 004-noise-sweep/spec.md
├── tests/
│   ├── test_quantum_engine.py
│   ├── test_noise_models.py
│   ├── test_database.py
│   └── test_api.py
├── docs/
├── pyproject.toml
└── uv.lock
```

---

## Specs

This project was developed using [spec-kit](https://github.com/thecodingwizard/spec-kit).
Each feature has a specification in `specs/`:

| Spec | Feature |
|---|---|
| [001-quantum-engine](specs/001-quantum-engine/spec.md) | 4-circuit Qiskit simulation engine |
| [002-noise-models](specs/002-noise-models/spec.md) | Depolarizing noise layer |
| [003-flask-api](specs/003-flask-api/spec.md) | REST API endpoints |
| [004-noise-sweep](specs/004-noise-sweep/spec.md) | Fidelity degradation sweep |

---

## License

[MIT](LICENSE)
