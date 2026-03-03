# Quantum Circuit Error Analyzer Dashboard - Master Specification

## Project Overview

The Quantum Circuit Error Analyzer Dashboard is a full-stack web application that lets users
simulate quantum circuits under realistic noise conditions and visualize how errors affect
quantum computation. Think of it as a "quantum lab in a browser" — you pick a circuit,
dial up the error rate, hit simulate, and see exactly how noise degrades the results.

### Goals

**Learning Goals:**
- Understand how quantum circuits work at a conceptual and code level
- Learn how real quantum computers fail due to noise
- Practice full-stack web development (Python backend + JS frontend)
- Get comfortable with REST APIs, databases, and data visualization
- Build a portfolio project that shows real technical depth

**Product Goals:**
- Working simulation of 4 quantum circuits
- Adjustable error rates (0% to 20%)
- Real-time visualization of measurement distributions
- Persistent history of past simulations
- Clean, professional UI

---

## Technical Architecture (ASCII Diagram)

```
+------------------+         HTTP/JSON         +------------------+
|                  |  ---------------------->  |                  |
|   FRONTEND       |                           |   FLASK API      |
|   (Browser)      |  <----------------------  |   (Python)       |
|                  |                           |                  |
|  - index.html    |   GET /api/circuits       |  - app.py        |
|  - app.js        |   POST /api/simulate      |  - /api routes   |
|  - styles.css    |   GET /api/results/<id>   |                  |
|  - Chart.js      |                           +--------+---------+
+------------------+                                    |
                                                        | calls
                                                        v
                                           +------------------+
                                           |  QUANTUM ENGINE  |
                                           |  (Qiskit)        |
                                           |                  |
                                           |  - quantum_      |
                                           |    engine.py     |
                                           |  - noise_        |
                                           |    models.py     |
                                           +--------+---------+
                                                    |
                                                    | reads/writes
                                                    v
                                           +------------------+
                                           |   SQLite DB      |
                                           |                  |
                                           |  - circuits      |
                                           |  - simulations   |
                                           |  - results       |
                                           +------------------+
```

---

## Technology Stack

| Technology | Role | Why We Chose It |
|---|---|---|
| **Python 3.11+** | Backend language | Industry standard for quantum computing and scientific computing |
| **Flask** | Web framework | Lightweight, easy to learn, great for APIs. Less magic than Django. |
| **Qiskit** | Quantum simulation | IBM's open-source quantum SDK. Industry standard. |
| **SQLite** | Database | No server setup needed, file-based, perfect for learning |
| **HTML5/CSS3** | Frontend structure & style | Foundation of all web UIs |
| **JavaScript (ES6+)** | Frontend logic | Runs in the browser, handles API calls and DOM updates |
| **Chart.js** | Data visualization | Simple, beautiful charts with minimal configuration |
| **Git** | Version control | Track changes, industry standard workflow |

---

## System Design

### Frontend Layer
The browser-based interface. Users interact here — they never touch the backend directly.
- **index.html**: Page structure (circuit selector, error slider, results panel)
- **app.js**: Handles button clicks, calls the Flask API, renders charts
- **styles.css**: Makes it look professional

### Backend Layer (Flask API)
The "brain" that receives requests from the frontend and coordinates everything.
- **app.py**: Defines API routes, validates input, orchestrates the simulation
- Receives HTTP requests, calls the quantum engine, saves results to DB, returns JSON

### Quantum Engine Layer
The science part — actually runs the quantum simulations.
- **quantum_engine.py**: Builds the 4 quantum circuits using Qiskit
- **noise_models.py**: Adds realistic error models to simulate real quantum hardware

### Database Layer (SQLite)
Persistent storage for simulation history.
- **database.py**: All database operations (create tables, insert results, query history)
- **quantum_circuits.db**: The actual SQLite database file (auto-created)

---

## Week-by-Week Implementation Plan

### WEEK 1: Backend (Days 1-7)

| Day | Phase | Task | Deliverable |
|---|---|---|---|
| 1-2 | Phase 1 | Quantum Engine | `quantum_engine.py` with 4 circuits |
| 3-4 | Phase 2 | Noise Models | `noise_models.py` with depolarizing errors |
| 4-5 | Phase 3 | Database | `database.py` with full schema |
| 6-7 | Phase 4 | Flask API | `app.py` with 3 endpoints |

### WEEK 2: Frontend (Days 8-14)

| Day | Phase | Task | Deliverable |
|---|---|---|---|
| 8-9 | Phase 5 | HTML Structure | `index.html` with all UI elements |
| 9-10 | Phase 6 | JavaScript Logic | `app.js` connecting to API |
| 11-12 | Phase 7 | Visualization | Chart.js bar charts for results |
| 13-14 | Phase 8 | Styling & Polish | `styles.css`, final UI cleanup |

---

## Success Criteria Per Phase

### Phase 1 (Quantum Engine)
- [ ] Can import Qiskit without errors
- [ ] Bell State circuit produces ~50% |00> and ~50% |11> results
- [ ] GHZ State circuit runs and returns valid measurements
- [ ] Quantum Teleportation circuit completes
- [ ] Grover's Algorithm circuit finds the marked state
- [ ] All circuits tested with `python quantum_engine.py`

### Phase 2 (Noise Models)
- [ ] Depolarizing noise model created for any error rate p
- [ ] Running Bell State with noise shows degraded results (more |01>, |10> states)
- [ ] Error rate 0.0 produces near-ideal results
- [ ] Error rate 0.1 shows visible degradation

### Phase 3 (Database)
- [ ] Tables created automatically on first run
- [ ] Can insert a simulation record
- [ ] Can retrieve simulation history
- [ ] Foreign keys enforced correctly

### Phase 4 (Flask API)
- [ ] `GET /api/circuits` returns list of 4 circuits as JSON
- [ ] `POST /api/simulate` runs simulation and returns results
- [ ] `GET /api/results/<id>` retrieves past simulation
- [ ] Error responses return proper HTTP status codes (400, 404, 500)
- [ ] API tested with curl commands

### Phase 5 (HTML)
- [ ] Circuit dropdown shows all 4 options
- [ ] Error rate slider works (0-20%)
- [ ] Simulate button present
- [ ] Results section exists
- [ ] Page is valid HTML (no console errors)

### Phase 6 (JavaScript)
- [ ] Click simulate → API call fires
- [ ] Loading state shown during simulation
- [ ] Results displayed after simulation
- [ ] Error messages shown on failure

### Phase 7 (Visualization)
- [ ] Bar chart renders with correct data
- [ ] Chart updates when new simulation runs
- [ ] Chart labels show quantum states (|00>, |01>, etc.)
- [ ] Ideal vs noisy comparison visible

### Phase 8 (Styling)
- [ ] Responsive on mobile and desktop
- [ ] Professional color scheme
- [ ] Clear visual hierarchy
- [ ] No layout bugs

---

## Testing Checklist

### Backend Tests
- [ ] `quantum_engine.py` — each circuit returns valid counts dict
- [ ] `noise_models.py` — noise increases error counts proportionally
- [ ] `database.py` — CRUD operations work
- [ ] `app.py` — each endpoint returns correct status codes

### Frontend Tests
- [ ] Page loads without console errors
- [ ] API calls reach backend
- [ ] Chart renders correctly
- [ ] Edge cases (error rate = 0, error rate = 20%)

### Integration Tests
- [ ] Full flow: select circuit → simulate → see chart
- [ ] Past results load from database
- [ ] Multiple simulations don't conflict

---

## Troubleshooting Guide

| Problem | Likely Cause | Fix |
|---|---|---|
| `ImportError: No module named 'qiskit'` | Not installed | `pip install qiskit qiskit-aer` |
| Flask 404 on API route | Route typo or wrong method | Check `app.py` route decorator |
| Chart doesn't render | JS error or empty data | Open browser console (F12) and check errors |
| SQLite "no such table" | DB not initialized | Call `init_db()` before any queries |
| CORS error in browser | Flask missing CORS headers | `pip install flask-cors`, add to `app.py` |
| Qiskit simulation slow | Too many shots | Reduce shots from 1024 to 512 |
| Empty measurement results | Circuit not measured | Add `measure_all()` to circuit |
