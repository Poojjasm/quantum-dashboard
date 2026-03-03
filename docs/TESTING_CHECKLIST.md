# Testing Checklist — Quantum Circuit Error Analyzer

> Testing isn't optional. Untested code has bugs — you just haven't found them yet.
> Work through each checklist section as you complete that phase.

---

## How to Use This File

Check off items as you verify them. If something fails, note it in LEARNING_LOG.md.
Don't move to the next phase until the current phase passes its tests.

---

## Week 1: Backend Tests

---

### Phase 1: Quantum Engine (`quantum_engine.py`)

**Environment Setup:**
- [ ] `python3 -c "import qiskit; print(qiskit.__version__)"` prints a version number
- [ ] `python3 -c "import qiskit_aer; print('aer ok')"` prints "aer ok"
- [ ] No import errors when running `python backend/quantum_engine.py`

**Bell State:**
- [ ] Returns a dict (not empty, not None)
- [ ] All keys are binary strings of length 2: "00", "01", "10", "11"
- [ ] Sum of all counts ≈ shots (within rounding)
- [ ] "00" count ≈ 50% of shots (no noise)
- [ ] "11" count ≈ 50% of shots (no noise)
- [ ] "01" count = 0 (no noise) — Bell State never produces "01" ideally
- [ ] "10" count = 0 (no noise)

**GHZ State:**
- [ ] Returns keys of length 3: "000", "001", etc.
- [ ] "000" ≈ 50% (no noise)
- [ ] "111" ≈ 50% (no noise)
- [ ] No other states appear (no noise)

**Grover's Algorithm:**
- [ ] "11" appears with ≥ 85% probability (no noise)
- [ ] Other states appear with low probability

**Dispatcher (`run_named_circuit`):**
- [ ] `run_named_circuit("bell", 0.0)` → valid Bell counts
- [ ] `run_named_circuit("ghz", 0.0)` → valid GHZ counts
- [ ] `run_named_circuit("teleportation", 0.0)` → no error
- [ ] `run_named_circuit("grover", 0.0)` → "11" dominant
- [ ] `run_named_circuit("invalid", 0.0)` → raises `ValueError`

**Manual test command:**
```bash
python backend/quantum_engine.py
# Check all 4 circuits print sensible output
```

---

### Phase 2: Noise Models (`noise_models.py`)

**Noise Model Construction:**
- [ ] `build_noise_model(0.0)` returns `None`
- [ ] `build_noise_model(0.05)` returns a `NoiseModel` object (not None)
- [ ] `build_noise_model(0.20)` returns a `NoiseModel` object

**Noise Effect Verification:**
- [ ] Bell at p=0.0: "01"+"10" counts < 5 (near zero errors)
- [ ] Bell at p=0.05: "01"+"10" counts > 30 (clearly more errors)
- [ ] Bell at p=0.10: "01"+"10" counts > 80
- [ ] Bell at p=0.20: "01"+"10" counts > 150
- [ ] Error counts increase monotonically as p increases

**Trend test (run this manually):**
```python
from quantum_engine import run_named_circuit
for p in [0.0, 0.05, 0.10, 0.20]:
    counts = run_named_circuit("bell", p)
    errors = counts.get("01", 0) + counts.get("10", 0)
    print(f"p={p}: error states = {errors}")
# Should print increasing error counts
```

**Ideal Counts:**
- [ ] `get_ideal_counts("bell", 1024)` returns `{"00": 512, "11": 512}`
- [ ] `get_ideal_counts("ghz", 1024)` returns `{"000": 512, "111": 512}`
- [ ] `get_ideal_counts("unknown", 1024)` returns `{}`

---

### Phase 3: Database (`database.py`)

**Setup:**
- [ ] `init_db()` runs without error
- [ ] Database file created at `data/quantum_circuits.db`
- [ ] Running `init_db()` twice doesn't error or duplicate data

**Circuits table:**
- [ ] 4 rows exist after init: bell, ghz, teleportation, grover
- [ ] Each row has correct num_qubits (2, 3, 3, 2)

**Save simulation:**
- [ ] `save_simulation("bell", 0.05, 1024, {"00": 467, "11": 507, "01": 28, "10": 22})` returns an integer
- [ ] That integer is the simulation_id (1, 2, 3, ...)
- [ ] Running twice returns incrementing IDs

**Get simulation:**
- [ ] `get_simulation(1)` returns a dict with 'simulation' and 'results' keys
- [ ] 'simulation' has: id, circuit_id, error_rate, shots, created_at
- [ ] 'results' is a list of dicts, each with 'state' and 'count'
- [ ] Sum of all result counts equals shots (1024)
- [ ] `get_simulation(99999)` returns `None`

**Get history:**
- [ ] `get_history(limit=5)` returns a list of at most 5 items
- [ ] Items are sorted newest first (by created_at DESC)
- [ ] `get_history(circuit_filter="bell")` returns only Bell simulations

**Database integrity:**
- [ ] Trying to insert simulation with circuit_id="fake" should fail (FK constraint)
- [ ] Deleting a simulation cascades to delete its results

---

### Phase 4: Flask API (`app.py`)

**Server startup:**
- [ ] `python backend/app.py` starts without errors
- [ ] Console shows: `Running on http://127.0.0.1:5000`
- [ ] No import errors

**GET /api/circuits:**
```bash
curl http://localhost:5000/api/circuits
```
- [ ] Returns HTTP 200
- [ ] Response has "circuits" key
- [ ] "circuits" is a list of 4 items
- [ ] Each item has: id, name, description, num_qubits, difficulty

**POST /api/simulate — success cases:**
```bash
# Bell State, 5% noise
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.05}'
```
- [ ] Returns HTTP 200
- [ ] Response has: simulation_id, circuit, error_rate, shots, counts, ideal_counts
- [ ] counts values are integers summing to ~1024
- [ ] simulation_id is a positive integer

- [ ] Works for all 4 circuits (test each one)
- [ ] Works with error_rate = 0.0 (no noise)
- [ ] Works with error_rate = 0.20 (max noise)
- [ ] Works with shots = 2048

**POST /api/simulate — error cases:**
```bash
# Missing circuit field
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"error_rate": 0.05}'
```
- [ ] Missing "circuit" → 400 with "MISSING_FIELD" code

```bash
# Invalid circuit name
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "shor", "error_rate": 0.05}'
```
- [ ] Invalid circuit → 400 with "INVALID_CIRCUIT" code

```bash
# Error rate too high
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.50}'
```
- [ ] Out-of-range error_rate → 422 with "OUT_OF_RANGE" code

**GET /api/results/\<id\>:**
```bash
curl http://localhost:5000/api/results/1
```
- [ ] Returns 200 with simulation data and results array
- [ ] results array has correct state/count pairs

```bash
curl http://localhost:5000/api/results/99999
```
- [ ] Returns 404 with "NOT_FOUND" code

**GET /api/history:**
```bash
curl http://localhost:5000/api/history
```
- [ ] Returns 200 with "simulations" list
- [ ] Newest simulation is first

---

## Week 2: Frontend Tests

---

### Phase 5: HTML Structure (`index.html`)

**Open in browser: `open frontend/index.html`**

- [ ] Page loads without blank screen
- [ ] No red errors in browser console (F12 → Console)
- [ ] Circuit dropdown is visible and has 4 options
- [ ] Error rate slider is visible and draggable
- [ ] Simulate button is visible and clickable
- [ ] Results section/panel is visible (even if empty)
- [ ] Page has a title (shown in browser tab)

**Accessibility:**
- [ ] All form elements have labels
- [ ] Page makes sense without CSS (disable in dev tools to test)

---

### Phase 6: JavaScript Logic (`app.js`)

**Basic functionality:**
- [ ] No errors in browser console on page load
- [ ] Slider value displays correctly (shows "0.05" as you drag)
- [ ] Circuit dropdown selection is reflected somewhere on page

**API integration (Flask must be running):**
- [ ] Clicking Simulate triggers a network request (check Network tab in F12)
- [ ] Loading state appears while waiting
- [ ] Loading state clears after response
- [ ] Results panel shows after successful simulation
- [ ] Console shows no unhandled promise rejections

**Error handling:**
- [ ] If Flask is not running: user sees friendly error message, not blank
- [ ] Error message clears on next successful simulation

---

### Phase 7: Chart.js Visualization

**Chart rendering:**
- [ ] Chart canvas is visible
- [ ] Chart renders with correct number of bars
- [ ] For Bell State: 4 bars (00, 01, 10, 11)
- [ ] For GHZ State: 8 bars (000 through 111)
- [ ] Bar labels use quantum notation (|00⟩, etc.)
- [ ] Y-axis shows count values
- [ ] Legend distinguishes ideal vs noisy bars

**Chart updates:**
- [ ] Running a second simulation updates the chart (doesn't create a second chart)
- [ ] Switching circuits updates bar count correctly

**Visual quality:**
- [ ] Chart is readable at normal zoom
- [ ] Bars don't overlap labels
- [ ] Colors are distinguishable

---

### Phase 8: Styling

- [ ] Page looks professional (not unstyled HTML)
- [ ] Color scheme is consistent
- [ ] Controls and results panel are clearly separated
- [ ] Fonts are readable
- [ ] Slider and dropdown are styled (not default browser style)

**Responsive (test with browser at 375px width):**
- [ ] No horizontal scroll bar
- [ ] Text doesn't overflow containers
- [ ] Chart is still visible
- [ ] Controls still usable

---

## Integration Tests (End-to-End)

These test the complete flow from browser to database and back.

**Test 1: Full simulation flow**
1. Open browser at `http://localhost:5000`
2. Select "Bell State" from dropdown
3. Set error rate to 5%
4. Click "Simulate"
5. Verify:
   - [ ] Loading indicator appeared briefly
   - [ ] Chart renders with results
   - [ ] Chart shows both "ideal" and "noisy" data
   - [ ] "00" and "11" are the tallest bars
   - [ ] "01" and "10" are small but non-zero

**Test 2: High noise degradation**
1. Select "Bell State", set error rate to 20%, simulate
2. Verify:
   - [ ] "01" and "10" bars are significantly larger than at 5%
   - [ ] Results look more random / less dominated by "00" and "11"

**Test 3: All circuits run**
For each circuit, run a simulation at 5% noise and verify chart renders:
- [ ] Bell State
- [ ] GHZ State
- [ ] Quantum Teleportation
- [ ] Grover's Algorithm

**Test 4: Retrieve history**
- [ ] After running 3+ simulations, history shows previous runs
- [ ] Clicking a past simulation loads its results

---

## Pre-Presentation Checklist

Do this the day before you show or submit the project:

**Functionality:**
- [ ] Backend starts with `python backend/app.py`
- [ ] Browser opens and shows the full dashboard
- [ ] All 4 circuits simulate successfully
- [ ] Charts display correctly
- [ ] History panel shows past simulations

**Code quality:**
- [ ] No `print()` debug statements left in production code
- [ ] No commented-out code blocks (unless intentional with explanation)
- [ ] No hardcoded paths or API URLs (use environment variables or config)

**Git:**
- [ ] All files committed and pushed to GitHub
- [ ] `git status` shows "nothing to commit"
- [ ] README.md accurately describes the project
- [ ] Commits have clear, conventional messages

**Documentation:**
- [ ] README.md installation steps work from scratch (test in a fresh directory)
- [ ] LEARNING_LOG.md filled in for all 14 days

**Final demo script:**
1. Show the GitHub repo (README, project structure)
2. Clone fresh and run `pip install -r requirements.txt`
3. Start `python backend/app.py`
4. Open browser, demo all 4 circuits at different noise levels
5. Explain what the chart is showing
6. Show the database has recorded everything
