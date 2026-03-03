# Project Timeline — 2-Week Schedule

## Overview

| Week | Focus | Goal |
|---|---|---|
| Week 1 (Days 1-7) | Backend | Working quantum simulation API |
| Week 2 (Days 8-14) | Frontend | Working browser dashboard |

**Total estimated hours:** 40-50 hours (3-4 hours/day)

---

## Week 1: Backend

---

### Day 1 — Environment Setup + Quantum Basics
**Estimated time:** 3-4 hours
**Phase:** Foundation

**Goals:**
- [ ] Read `QUANTUM_CONCEPTS.md` completely (1 hour)
- [ ] Follow `PROJECT_SETUP.md` to set up environment (1 hour)
- [ ] Install Python, venv, Qiskit
- [ ] Write and run "Hello Quantum World" (Bell State test in Python REPL)
- [ ] Understand what H gate and CNOT gate do

**Hour-by-hour breakdown:**
- Hour 1: Read QUANTUM_CONCEPTS.md (qubits through superposition section)
- Hour 2: Set up virtual environment, install dependencies
- Hour 3: Follow Qiskit quickstart, run your first 3-line circuit in REPL
- Hour 4: Write the Bell State function, run it, study the output

**"Done" looks like:**
```python
# This runs without errors and produces sensible output
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()
sim = AerSimulator()
from qiskit import transpile
job = sim.run(transpile(circuit, sim), shots=100)
print(job.result().get_counts())
# {'00': ~50, '11': ~50}
```

**Git commit:**
```
chore: initialize project with environment setup
```

---

### Day 2 — Quantum Engine: All 4 Circuits
**Estimated time:** 4-5 hours
**Phase:** Phase 1 (continued)

**Goals:**
- [ ] Complete `backend/quantum_engine.py` with all 4 circuits
- [ ] Each circuit produces expected output when run
- [ ] Add `run_named_circuit()` dispatcher function
- [ ] Test all 4 circuits from command line

**Hour-by-hour breakdown:**
- Hour 1: Build `build_bell_circuit()` and test
- Hour 2: Build `build_ghz_circuit()` and test
- Hour 3: Build `build_teleportation_circuit()` — this one is complex, read docs
- Hour 4: Build `build_grover_circuit()` — study the oracle + diffuser
- Hour 5: Add `run_named_circuit()`, test all 4, fix any issues

**Expected circuit outputs:**
```
Bell:          {'00': ~512, '11': ~512}
GHZ:           {'000': ~512, '111': ~512}
Teleportation: q2 reflects initial q0 state
Grover:        {'11': ~976, others small}
```

**Git commit:**
```
feat: implement 4 quantum circuits with Qiskit
```

---

### Day 3 — Noise Models
**Estimated time:** 3-4 hours
**Phase:** Phase 2

**Goals:**
- [ ] Complete `backend/noise_models.py`
- [ ] Bell State at error_rate=0.0 → ~perfect results
- [ ] Bell State at error_rate=0.1 → clearly degraded results
- [ ] Understand the depolarizing error model intuitively

**Hour-by-hour breakdown:**
- Hour 1: Read Qiskit Aer noise model docs, understand `NoiseModel` class
- Hour 2: Implement `build_noise_model(error_rate)` for single and 2-qubit gates
- Hour 3: Test with increasing error rates (0.0, 0.05, 0.10, 0.20), observe degradation
- Hour 4: Add `get_ideal_counts()` for reference comparison, document the file

**Experiment to run:**
```python
for p in [0.0, 0.01, 0.05, 0.10, 0.20]:
    counts = run_named_circuit("bell", p)
    errors = counts.get("01", 0) + counts.get("10", 0)
    print(f"p={p:.2f}: error states = {errors}/1024 ({100*errors/1024:.1f}%)")
```

**Git commit:**
```
feat: add depolarizing noise models to all circuits
```

---

### Day 4 — Database: Schema + Implementation
**Estimated time:** 4 hours
**Phase:** Phase 3

**Goals:**
- [ ] Read `DATABASE_SCHEMA.md` completely (30 min)
- [ ] Complete `backend/database.py`
- [ ] Tables auto-create on first run
- [ ] Can insert and retrieve a simulation

**Hour-by-hour breakdown:**
- Hour 1: Read DATABASE_SCHEMA.md, sketch the tables on paper/notes
- Hour 2: Implement `init_db()` and `seed_circuits()`
- Hour 3: Implement `save_simulation()` — inserts into simulations + results tables
- Hour 4: Implement `get_simulation()` and `get_history()`, test all functions

**Quick test (run in Python REPL):**
```python
import sys
sys.path.insert(0, 'backend')
from database import init_db, save_simulation, get_simulation

init_db()
sim_id = save_simulation("bell", 0.05, 1024, {"00": 467, "11": 507, "01": 28, "10": 22})
print(f"Saved simulation: {sim_id}")

result = get_simulation(sim_id)
print(result)
```

**Git commit:**
```
feat: implement SQLite database schema and CRUD operations
```

---

### Day 5 — Database: Testing + Edge Cases
**Estimated time:** 3 hours
**Phase:** Phase 3 (wrap-up)

**Goals:**
- [ ] Write simple tests for all database functions
- [ ] Handle edge cases (what if simulation_id doesn't exist?)
- [ ] Verify foreign keys work (can't add simulation for unknown circuit)
- [ ] Create `tests/test_database.py`

**Hour-by-hour breakdown:**
- Hour 1: Write tests for `init_db()` and `seed_circuits()`
- Hour 2: Write tests for `save_simulation()` and `get_simulation()`
- Hour 3: Write tests for `get_history()`, test edge cases, fix any bugs

**Git commit:**
```
test: add unit tests for database operations
```

---

### Day 6 — Flask API: Routes + Request Handling
**Estimated time:** 4-5 hours
**Phase:** Phase 4

**Goals:**
- [ ] Read `API_REFERENCE.md` completely (30 min)
- [ ] Complete `backend/app.py` with all 4 routes
- [ ] Server starts without errors
- [ ] `GET /api/circuits` returns correct JSON

**Hour-by-hour breakdown:**
- Hour 1: Read API_REFERENCE.md, understand REST concepts
- Hour 2: Set up Flask app, add CORS, implement `GET /api/circuits`
- Hour 3: Implement `POST /api/simulate` with input validation
- Hour 4: Implement `GET /api/results/<id>` and `GET /api/history`
- Hour 5: Test all routes manually with curl

**Start server and test:**
```bash
python backend/app.py

# In another terminal:
curl http://localhost:5000/api/circuits
```

**Git commit:**
```
feat: create Flask REST API skeleton with 4 endpoints
```

---

### Day 7 — Flask API: Integration + Testing
**Estimated time:** 4 hours
**Phase:** Phase 4 (wrap-up)

**Goals:**
- [ ] Full end-to-end test: request → quantum engine → database → response
- [ ] All 4 circuits simulate successfully via API
- [ ] Error responses work correctly (400, 404, 500)
- [ ] Write API integration tests in `tests/test_api.py`

**Hour-by-hour breakdown:**
- Hour 1: Run all curl commands from API_REFERENCE.md, fix issues
- Hour 2: Test error cases (invalid circuit, out-of-range error_rate, bad JSON)
- Hour 3: Write test_api.py with automated tests
- Hour 4: Fix any bugs found, document known limitations

**End of Week 1 checkpoint:** The backend is done. You should be able to:
1. Start the Flask server
2. Hit `POST /api/simulate` with curl
3. Get back measurement counts
4. See those counts saved in the SQLite database

**Git commit:**
```
feat: connect quantum engine to API and complete backend integration
```

---

## Week 2: Frontend

---

### Day 8 — HTML Structure
**Estimated time:** 3-4 hours
**Phase:** Phase 5

**Goals:**
- [ ] Complete `frontend/index.html` with all UI elements
- [ ] Circuit dropdown with 4 options
- [ ] Error rate slider (0-20%)
- [ ] Simulate button
- [ ] Results panel with chart canvas
- [ ] History section
- [ ] Page valid HTML (no errors in browser console)

**Git commit:**
```
feat: create frontend HTML structure
```

---

### Day 9 — JavaScript Logic + API Integration
**Estimated time:** 4-5 hours
**Phase:** Phase 6

**Goals:**
- [ ] `frontend/static/js/app.js` complete
- [ ] Clicking Simulate calls `POST /api/simulate`
- [ ] Loading state shown during simulation
- [ ] Results panel updates with returned data
- [ ] Error messages displayed on failure

**Key JavaScript concepts needed:**
- `document.getElementById()` — get DOM elements
- `element.addEventListener()` — handle button clicks
- `fetch()` with async/await — call Flask API
- JSON parsing: `await response.json()`

**Git commit:**
```
feat: implement JavaScript frontend logic and API integration
```

---

### Day 10 — Chart.js Visualization
**Estimated time:** 3-4 hours
**Phase:** Phase 7

**Goals:**
- [ ] Bar chart renders with measurement results
- [ ] Ideal vs noisy bars shown side by side
- [ ] Quantum state labels (|00⟩, |01⟩, etc.)
- [ ] Chart updates when new simulation runs
- [ ] Chart is readable and well-labeled

**Git commit:**
```
feat: add Chart.js measurement distribution visualization
```

---

### Day 11 — CSS Styling
**Estimated time:** 4 hours
**Phase:** Phase 8

**Goals:**
- [ ] Dark theme or professional color scheme
- [ ] Grid layout: controls left, results right
- [ ] Slider and dropdown styled nicely
- [ ] Responsive (looks good on mobile too)
- [ ] Loading animation (spinner or shimmer)

**Git commit:**
```
feat: add professional CSS styling and dark theme
```

---

### Day 12 — Error Handling + Edge Cases
**Estimated time:** 3 hours
**Phase:** Polish

**Goals:**
- [ ] What happens if Flask is not running? (Show user-friendly message)
- [ ] What happens if error_rate = 0? (Shows perfect results)
- [ ] What happens if error_rate = 20%? (Shows very noisy results)
- [ ] Loading state clears after error
- [ ] Input validation on frontend (match backend rules)

**Git commit:**
```
fix: add comprehensive error handling and input validation
```

---

### Day 13 — Final Testing + Bug Fixes
**Estimated time:** 4 hours
**Phase:** QA

**Goals:**
- [ ] Complete TESTING_CHECKLIST.md manually
- [ ] Test all 4 circuits at 0%, 5%, 10%, 20% error rates
- [ ] Test on mobile (browser dev tools → responsive mode)
- [ ] Fix all identified bugs
- [ ] Check browser console for errors

**Git commit:**
```
fix: resolve issues found during final testing pass
```

---

### Day 14 — Documentation + Launch
**Estimated time:** 3 hours
**Phase:** Wrap-up

**Goals:**
- [ ] Update README.md project status to all phases complete
- [ ] Fill in personal sections of LEARNING_LOG.md
- [ ] Final commit and push to GitHub
- [ ] Demo the app end-to-end one final time
- [ ] Write Day 14 learning log entry

**Git commits:**
```
docs: finalize README and update project status
chore: final cleanup and remove debug code
```

---

## Milestone Summary

| Milestone | Day | What You Have |
|---|---|---|
| Environment ready | End of Day 1 | Qiskit installed, first circuit running |
| Quantum engine | End of Day 2 | All 4 circuits working |
| Noise models | End of Day 3 | Error-rate-controlled simulation |
| Database | End of Day 5 | Persistent storage working |
| Backend complete | End of Day 7 | Full API, tested with curl |
| HTML structure | End of Day 8 | Page renders in browser |
| API connected | End of Day 9 | Clicking button calls Flask |
| Charts working | End of Day 10 | Results visualized |
| Styled | End of Day 11 | Professional-looking dashboard |
| **Project DONE** | End of Day 14 | Full working app on GitHub |

---

## If You Fall Behind

**1 day behind:** Work a longer day (5+ hours) to catch up. Skip optional edge case testing.

**2 days behind:** Cut scope. History panel is optional. Focus on: simulate → chart.

**3+ days behind:** Talk to your instructor/accountability partner. Reset expectations.

**Most common time sinks to avoid:**
- Getting stuck on quantum math (you don't need the full math to code this)
- Trying to make CSS perfect before functionality works
- Debugging without reading error messages carefully
- Not committing often (makes debugging much harder)
