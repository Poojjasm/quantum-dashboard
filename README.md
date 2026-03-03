# Quantum Circuit Error Analyzer Dashboard

> A full-stack web app that simulates quantum circuits under realistic noise conditions
> and visualizes how errors degrade quantum computation — built as a 2-week learning project.

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0-000000?style=flat&logo=flask)](https://flask.palletsprojects.com/)
[![Qiskit](https://img.shields.io/badge/Qiskit-0.45-6929C4?style=flat&logo=qiskit)](https://qiskit.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Progress-orange)](LEARNING_LOG.md)

---

## What This Project Does

Real quantum computers are powerful but **noisy**. Qubits lose their quantum properties
due to heat, vibrations, and electromagnetic interference — a process called **decoherence**.

This dashboard lets you explore that problem interactively:

1. **Pick a quantum circuit** — Bell State, GHZ State, Quantum Teleportation, or Grover's Algorithm
2. **Set an error rate** — from 0% (perfect, theoretical) to 20% (very noisy)
3. **Hit Simulate** — Qiskit runs the circuit with your noise level
4. **See the results** — bar chart shows measurement distribution vs ideal

The visual difference between the ideal and noisy results is exactly what thousands of
quantum researchers are working to minimize.

---

## Features

- **4 Quantum Circuits** — Bell State, GHZ State, Quantum Teleportation, Grover's Algorithm
- **Adjustable Noise** — Depolarizing error model, 0–20% error rate slider
- **Live Visualization** — Chart.js bar charts updating in real time
- **Simulation History** — All past runs saved to SQLite database
- **REST API** — Clean Flask endpoints for circuit selection and simulation
- **Educational UI** — Every circuit has an explanation for learners

---

## Tech Stack

| Layer | Technology | Why We Chose It |
|---|---|---|
| **Quantum Engine** | Qiskit + Aer | IBM's open-source quantum SDK — industry standard |
| **Backend API** | Flask (Python) | Lightweight, easy to learn, perfect for REST APIs |
| **Database** | SQLite | Zero-setup, file-based — no separate server needed |
| **Frontend** | HTML5 + Vanilla JS | No framework complexity — pure fundamentals |
| **Visualization** | Chart.js | Beautiful charts with minimal configuration |
| **Version Control** | Git + GitHub | Industry-standard workflow |

---

## Quick Start

### Prerequisites

- Python 3.11 or higher
- pip (Python package manager)
- Git

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/Poojjasm/quantum-dashboard.git
cd quantum-dashboard

# 2. Create a virtual environment (isolated Python sandbox)
python -m venv venv

# 3. Activate the virtual environment
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows

# 4. Install Python dependencies
pip install -r requirements.txt

# 5. Run the Flask backend
python backend/app.py
```

Open your browser to `http://localhost:5000` and start simulating!

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/api/circuits` | Returns list of all 4 available circuits |
| `POST` | `/api/simulate` | Runs a simulation with specified circuit + error rate |
| `GET` | `/api/results/<id>` | Retrieves a past simulation by ID |
| `GET` | `/api/history` | Returns last 20 simulations |

**Example request:**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.05, "shots": 1024}'
```

See [API Reference](docs/API_REFERENCE.md) for full documentation.

---

## Project Structure

```
quantum-dashboard/
├── backend/
│   ├── quantum_engine.py   # Qiskit circuit definitions
│   ├── noise_models.py     # Depolarizing noise models
│   ├── database.py         # SQLite CRUD operations
│   └── app.py              # Flask REST API
├── frontend/
│   ├── index.html          # Single-page UI
│   └── static/
│       ├── js/app.js       # API calls + Chart.js rendering
│       └── css/styles.css  # Styling
├── docs/                   # Full specification kit (read these first!)
├── tests/                  # Automated tests
├── data/                   # SQLite database (auto-created)
├── requirements.txt
└── LEARNING_LOG.md         # Day-by-day learning journal
```

---

## Documentation

All detailed documentation lives in `/docs`:

| Document | Description |
|---|---|
| [SPEC_KIT.md](docs/SPEC_KIT.md) | Master specification, architecture, success criteria |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | System design, data flow, component diagrams |
| [QUANTUM_CONCEPTS.md](docs/QUANTUM_CONCEPTS.md) | Quantum computing 101 — read before coding |
| [IMPLEMENTATION_GUIDE.md](docs/IMPLEMENTATION_GUIDE.md) | Phase-by-phase build instructions |
| [API_REFERENCE.md](docs/API_REFERENCE.md) | Complete API docs with curl examples |
| [DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md) | Database design and SQL statements |
| [TIMELINE.md](docs/TIMELINE.md) | 2-week daily schedule with hour estimates |
| [TESTING_CHECKLIST.md](docs/TESTING_CHECKLIST.md) | Testing strategy and QA checklist |
| [PROJECT_SETUP.md](docs/PROJECT_SETUP.md) | Detailed environment setup guide |
| [LEARNING_RESOURCES.md](docs/LEARNING_RESOURCES.md) | Curated reading list by topic |

**Start with:** [`docs/QUANTUM_CONCEPTS.md`](docs/QUANTUM_CONCEPTS.md) → then [`docs/PROJECT_SETUP.md`](docs/PROJECT_SETUP.md)

---

## Project Status

**Week 1 — Backend** *(In Progress)*
- [ ] Phase 1: Quantum Engine (Days 1-2)
- [ ] Phase 2: Noise Models (Days 3-4)
- [ ] Phase 3: Database (Days 4-5)
- [ ] Phase 4: Flask API (Days 6-7)

**Week 2 — Frontend** *(Planned)*
- [ ] Phase 5: HTML Structure (Days 8-9)
- [ ] Phase 6: JavaScript Logic (Days 9-10)
- [ ] Phase 7: Chart.js Visualization (Days 11-12)
- [ ] Phase 8: Styling & Polish (Days 13-14)

See [LEARNING_LOG.md](LEARNING_LOG.md) for daily progress updates.

---

## About

Built as a vibe coding project to explore:
- **Quantum computing fundamentals** (Qiskit, noise models, circuit design)
- **Full-stack web development** (Flask REST API + vanilla JS frontend)
- **Data visualization** (Chart.js)
- **Database design** (SQLite schema design)

The learning journey is documented day-by-day in [LEARNING_LOG.md](LEARNING_LOG.md).

---

## License

[MIT](LICENSE) — free to use, modify, and share.
