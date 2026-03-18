# Learning Log — Quantum Circuit Error Analyzer Dashboard

## How to Use This Log

Write in this log at the END of each work session.
Be honest — "still confused about X" is more useful than pretending everything clicked.
This log tracks your growth as an engineer, not just the code.

**Rule:** Always write at least 3 bullets under "What I learned" before closing your laptop.

---

## Day 1 — 2026-03-02
**Phase:** Environment Setup + Quantum Basics
**Time spent:** 2 hours
**Commits made:**
- [x] `chore: initialize project structure`
- [x] `docs: add complete specification kit (10 documents)`
- [x] `docs: add README and 14-day learning log template`

### What I learned:
- How to structure a full-stack Python + JS project from scratch
- What spec-kit is and why writing specs before code saves time
- Quantum computing basics: qubits are like coins spinning in the air — you don't know heads or tails until you catch it (measure it)

### What clicked:
- The difference between a classical bit (always 0 or 1) and a qubit (can be *both* until measured) finally made sense through the coin analogy
- Why we need a database: without it every simulation result disappears when the server restarts

### Still confused about:
- What exactly a "Hadamard gate" does mathematically — I understand it creates superposition but not the linear algebra behind it
- How Qiskit's AerSimulator actually works under the hood

### Resources used:
- Qiskit documentation — https://docs.quantum.ibm.com
- "Quantum Computing for Computer Scientists" (YouTube lecture)

### Code I wrote today:
```python
# First project file — just the folder structure
# backend/app.py, quantum_engine.py, noise_models.py, database.py
# frontend/index.html, static/js/app.js, static/css/styles.css
```

### Tomorrow's goals:
- Install Qiskit and actually run a Bell State circuit
- Understand H gate + CNOT well enough to explain it to someone else

---

## Day 2 — 2026-03-02
**Phase:** Quantum Engine — Building the 4 Circuits
**Time spent:** 3 hours
**Commits made:**
- [x] `feat: implement quantum circuits with Qiskit`

### What I learned:
- How to build a Bell State: H gate on qubit 0, then CNOT(0→1) creates entanglement
- GHZ state extends Bell to 3 qubits by chaining CNOTs
- Grover's Algorithm uses an "oracle" (CZ gate) to mark the target, then a "diffuser" to amplify it — with 2 qubits it finds |11⟩ with 100% probability in just 1 iteration
- `transpile()` in Qiskit is like a compiler — it converts high-level gates to what the simulator actually understands

### What clicked:
- Bell State: after H+CNOT, measuring qubit 0 *instantly* determines qubit 1, even if they were miles apart. That's entanglement.
- Why `measure_all()` is needed — without measurement the circuit runs but you get no classical output

### Still confused about:
- Quantum teleportation's classical correction step — why does Bob need Alice's measurement result if the state was already "transferred"?
- Why Grover's only needs 1 iteration for 2 qubits but needs √N iterations for N items

### Resources used:
- Qiskit tutorials — "Hello Qiskit" and "Grover's Algorithm"
- IBM Quantum Learning platform

### Code I wrote today:
```python
def build_bell_circuit() -> QuantumCircuit:
    circuit = QuantumCircuit(2, 2)
    circuit.h(0)       # superposition on qubit 0
    circuit.cx(0, 1)   # entangle qubit 1 with qubit 0
    circuit.measure(0, 0)
    circuit.measure(1, 1)
    return circuit
```

### Tomorrow's goals:
- Build the noise models so simulations look realistic
- Test all 4 circuits produce the right ideal distributions

---

## Day 3 — 2026-03-12
**Phase:** Noise Models — Depolarizing Errors
**Time spent:** 2 hours
**Commits made:**
- [x] `feat: add depolarizing noise models to quantum circuits`

### What I learned:
- Depolarizing noise: every gate has a probability `p` of applying a random Pauli error (X, Y, or Z flip)
- Two-qubit gates (CNOT, CZ) are physically harder to execute than single-qubit gates — they have ~2× the error rate in real hardware
- `qiskit_aer.noise.depolarizing_error(p, num_qubits)` creates the error channel

### What clicked:
- Why returning `None` for `error_rate=0` is cleaner than building an empty noise model — AerSimulator runs faster on the ideal path
- The "depolarizing channel" is the standard noise model used in research papers — this is real physics, not made up

### Still confused about:
- The exact math behind why 2-qubit gates are noisier — something about needing to physically couple the qubits together
- Why capping the two-qubit rate at 0.99 instead of 1.0 (p=1 is apparently "unphysical")

### Resources used:
- Qiskit Aer noise module documentation
- IBM research paper on quantum error rates

### Code I wrote today:
```python
def build_noise_model(error_rate: float) -> NoiseModel | None:
    if error_rate <= 0.0:
        return None
    noise_model = NoiseModel()
    single_qubit_error = depolarizing_error(error_rate, 1)
    two_qubit_error = depolarizing_error(min(error_rate * 2, 0.99), 2)
    noise_model.add_all_qubit_quantum_error(single_qubit_error, ['h', 'x', 'z'])
    noise_model.add_all_qubit_quantum_error(two_qubit_error, ['cx', 'cz'])
    return noise_model
```

### Tomorrow's goals:
- Design the SQLite database schema (3 tables)
- Implement save/load simulation operations

---

## Day 4 — 2026-03-12
**Phase:** Database Schema + database.py
**Time spent:** 2 hours
**Commits made:**
- [x] `feat: implement SQLite database schema and CRUD operations`

### What I learned:
- SQLite is built into Python — no server, no install, just `import sqlite3`
- Foreign keys are NOT enforced in SQLite by default — you need `PRAGMA foreign_keys = ON` per connection
- `row_factory = sqlite3.Row` lets you access columns by name (`row['id']`) instead of index (`row[0]`) — much cleaner
- `INSERT OR IGNORE` lets you re-run `init_db()` without duplicating data

### What clicked:
- Why using a transaction for `save_simulation` matters: if inserting result rows fails halfway through, the whole simulation row rolls back. No partial/corrupt data.
- `lastrowid` — after an INSERT, SQLite tells you what auto-increment ID it assigned. That's how we return `simulation_id` to Flask.

### Still confused about:
- When to use JOIN vs separate queries — I used JOIN here because it's one query but it makes the SQL more complex
- SQLite's `ON DELETE CASCADE` — I added it but didn't fully test that deleting a simulation removes its results

### Resources used:
- Python sqlite3 docs
- SQLite Tutorial website

### Code I wrote today:
```python
def save_simulation(circuit_id, error_rate, shots, counts):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO simulations (circuit_id, error_rate, shots) VALUES (?, ?, ?)",
            (circuit_id, error_rate, shots),
        )
        simulation_id = cursor.lastrowid
        result_rows = [(simulation_id, state, count) for state, count in counts.items()]
        cursor.executemany(
            "INSERT INTO results (simulation_id, state, count) VALUES (?, ?, ?)",
            result_rows,
        )
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
    return simulation_id
```

### Tomorrow's goals:
- Build the Flask REST API and connect it to the quantum engine and database
- Test all endpoints with curl

---

## Day 5 — 2026-03-12
**Phase:** Flask API — Routes + Request Handling
**Time spent:** 3 hours
**Commits made:**
- [x] `feat: create Flask REST API with 4 endpoints`

### What I learned:
- Flask routes use decorators: `@app.route("/api/simulate", methods=["POST"])`
- `request.get_json(silent=True)` parses JSON body — `silent=True` returns `None` instead of crashing on bad input
- CORS (Cross-Origin Resource Sharing): browsers block JS from calling APIs on different ports. `flask-cors` fixes this.
- Consistent error responses matter — every error in the API returns `{"error": "...", "code": "..."}` so the frontend can handle them programmatically
- macOS reserves port 5000 for AirPlay Receiver — I had to use port 5001

### What clicked:
- The validation chain in `api_simulate`: check body exists → check circuit field → validate circuit name → check error_rate → validate range → check shots. Each step returns early with a clear error.
- Why `_error()` is a helper function: instead of repeating `jsonify({...}), status` everywhere, one function handles all error responses consistently

### Still confused about:
- Gunicorn vs Flask dev server — I know Flask's built-in server is "not for production" but I don't fully understand why
- How `send_from_directory` serves the frontend — I get that Flask can serve static files but the path setup confused me

### Resources used:
- Flask documentation — quickstart and request handling
- MDN — CORS explained

### Code I wrote today:
```python
@app.route("/api/simulate", methods=["POST"])
def api_simulate():
    body = request.get_json(silent=True)
    if not body or not isinstance(body, dict):
        return _error("Request body must be valid JSON.", "BAD_REQUEST", 400)

    circuit_name = body.get("circuit")
    if not circuit_name:
        return _error("'circuit' is required.", "MISSING_FIELD", 400)
    if circuit_name not in VALID_CIRCUITS:
        return _error(f"Invalid circuit '{circuit_name}'.", "INVALID_CIRCUIT", 400)
    # ... more validation ...
    counts = run_named_circuit(circuit_name, error_rate, shots)
    simulation_id = save_simulation(circuit_name, error_rate, shots, counts)
    return jsonify({"simulation_id": simulation_id, "counts": counts, ...})
```

### Tomorrow's goals:
- Migrate frontend to React for a better component structure
- Get the full simulation flow working end-to-end in the browser

---

## Day 6 — 2026-03-12
**Phase:** React Frontend + Vite Setup
**Time spent:** 3 hours
**Commits made:**
- [x] `feat: migrate frontend to React (Vite) with Vercel/Railway deployment`

### What I learned:
- React components split the UI into reusable pieces: ControlsPanel, ResultsPanel, HistoryPanel, FidelityChart
- Custom hooks (`useSimulation.js`) keep all API logic in one place — components just call `runSimulation()` and get back `result`, `loading`, `error`
- Vite is much faster than Create React App — hot reload is nearly instant
- `useState` and `useEffect` — state triggers re-renders, effects run side-effects like fetch calls

### What clicked:
- The data flow: user clicks "Run" → `handleSubmit` in ControlsPanel → `onRun` callback → `runSimulation` in the hook → fetch POST → `setResult(data)` → ResultsPanel re-renders with new data
- Why `useCallback` on `runSimulation` prevents infinite re-render loops when it's in `useEffect` dependencies

### Still confused about:
- When to use `useCallback` vs `useMemo` — I used `useCallback` for all functions but I'm not sure when it actually matters for performance
- How Vite's proxy works in development — it magically forwards `/api/*` to localhost:5001 but I don't fully understand how

### Resources used:
- React docs (react.dev) — especially the hooks reference
- Vite docs — proxy configuration

### Code I wrote today:
```jsx
export function useSimulation() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const runSimulation = useCallback(async ({ circuit, error_rate, shots }) => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch('/api/simulate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ circuit, error_rate, shots }),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.error || `Server error ${response.status}`)
      setResult(data)
    } catch (err) {
      setError(err.message || 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [])

  return { result, loading, error, runSimulation }
}
```

### Tomorrow's goals:
- Add clickable history panel so users can reload past simulations
- Add noise preset buttons (Ideal / Low / Moderate / High / Extreme)

---

## Day 7 — 2026-03-12
**Phase:** History Panel + Noise Presets + Load Past Simulation
**Time spent:** 2 hours
**Commits made:**
- [x] `feat: add clickable history, noise presets, and load-past-simulation`
- [x] `feat: add noise sweep with fidelity degradation line chart`

### What I learned:
- "Controlled from outside" React pattern: `ControlsPanel` holds its own `circuit`/`errorRate` state, but `loadParams` prop from the parent can override it via `useEffect`
- Loading a past simulation requires two API calls: `GET /api/results/<id>` to get the counts, then `POST /api/simulate` with `error_rate=0` to get the ideal reference
- A noise sweep is just 8 sequential `POST /api/simulate` calls — running them one at a time lets you update a progress counter live

### What clicked:
- Why the noise sweep runs sequentially instead of in parallel: `Promise.all` would fire all 8 at once and you'd lose the live progress update. Sequential `await` inside a for loop shows "3 of 8 complete..."
- Fidelity formula: (shots that landed on ideal states / total shots) × 100 — simple but meaningful

### Week 1 Reflection:
**What's the biggest thing I learned this week?**
Quantum computing is harder to understand conceptually than it is to code. Once I stopped trying to visualize qubits as physical objects and just accepted the math (probabilities, gates, measurement collapse), the code made sense. The Qiskit API is actually very clean.

**What was harder than I expected?**
CORS. I expected it to "just work" but the browser's security policy blocked my React app from calling the Flask API. Spent a couple hours debugging before understanding the origin whitelist approach.

**What was easier than I expected?**
SQLite. I was scared of databases but `import sqlite3` and three tables was all I needed. No server setup, no connection strings, no migrations.

**Am I on track for Week 2?**
Yes — the full backend is done and the React frontend is functional. Week 2 is polish, deployment, and tests.

---

## Day 8 — 2026-03-12
**Phase:** CSS Styling + Techy Design
**Time spent:** 2 hours
**Commits made:**
- [x] `feat: CSS polish, animations, mobile layout, production CORS (Phase 8)`
- [x] `style: techy redesign with Orbitron/Outfit/Space Mono fonts`

### What I learned:
- CSS custom properties (`--color-primary`, `--font-display`) make theming consistent across the whole app
- Google Fonts: Orbitron (sci-fi display), Outfit (clean body), Space Mono (monospace numbers)
- `@keyframes` for animations: `fadeSlideIn`, `atomSpin`, `shimmer`
- `@media (prefers-reduced-motion: reduce)` — accessibility best practice to disable animations for users who need it
- `clamp(min, preferred, max)` for responsive font sizes that scale with viewport without media queries

### What clicked:
- CSS dot-grid background using `radial-gradient` — 1px dots on a 28px grid, subtly quantum/circuit-board looking
- Gradient text with `-webkit-background-clip: text` — the title color effect

### Still confused about:
- Why `box-shadow` glow effects use `rgba` with very low opacity — I just copied values that looked good rather than understanding the math
- CSS stacking contexts and `z-index` — still sometimes have to trial-and-error to get layers right

### Resources used:
- CSS-Tricks — custom properties guide
- Google Fonts
- MDN — `clamp()` reference

### Code I wrote today:
```css
body {
  background-color: var(--color-bg);
  background-image: radial-gradient(rgba(124, 111, 255, 0.12) 1px, transparent 1px);
  background-size: 28px 28px;
}

.app-title {
  font-family: var(--font-display);
  background: linear-gradient(135deg, #fff 0%, var(--color-accent) 50%, var(--color-accent-2) 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}
```

### Tomorrow's goals:
- Deploy Flask backend to Railway
- Deploy React frontend to Vercel
- Get the full production app working

---

## Day 9 — 2026-03-12
**Phase:** Deployment — Railway + Vercel
**Time spent:** 3 hours
**Commits made:**
- [x] `fix: update vercel.json rewrite to point to Railway URL`
- [x] `fix: restore secure CORS with ALLOWED_ORIGINS env var`
- [x] `fix: preset buttons font scales with panel width so labels never clip`

### What I learned:
- Railway deploys Python apps from GitHub using a `Procfile`: `web: gunicorn --chdir backend app:app --bind 0.0.0.0:$PORT`
- Vercel deploys React/Vite from the `frontend/` directory using `vercel.json` with `buildCommand` and `outputDirectory`
- Vercel proxy rewrites: `{"source": "/api/(.*)", "destination": "https://...railway.app/api/$1"}` — the request goes through Vercel's servers, so the browser never makes a cross-origin request. No CORS needed.
- `ALLOWED_ORIGINS` environment variable in Railway locks down which domains can call the API directly
- `python-dotenv` loads `.env` in development; Railway injects env vars directly in production

### What clicked:
- The two-server architecture: Flask on Railway handles computation, React on Vercel handles the UI. They communicate via the Vercel proxy.
- Why the proxy approach is cleaner than CORS: instead of fighting browser security, route all API calls through your own domain

### Still confused about:
- What Gunicorn "workers" are and how many to use — I used the default and it worked
- Railway's sleep behavior on the free tier — sometimes the first request is slow because the server "woke up"

### Resources used:
- Railway docs — Python deployment
- Vercel docs — rewrites configuration

### Code I wrote today:
```json
{
  "rewrites": [
    {
      "source": "/api/(.*)",
      "destination": "https://web-production-187b7.up.railway.app/api/$1"
    }
  ]
}
```

### Tomorrow's goals:
- Audit and fix all error handling edge cases
- Make sure the app doesn't crash on bad/unexpected data

---

## Day 10 — 2026-03-12
**Phase:** Error Handling Audit + Critical Fixes
**Time spent:** 2 hours
**Commits made:**
- [x] `Fix all Critical/High error handling issues from audit`

### What I learned:
- Defensive programming: always treat external data as potentially null/undefined before using it
- `obj?.property` optional chaining in JS prevents "Cannot read property of undefined" crashes
- Division by zero is a real bug — if `shots === 0` for any reason, every percentage calculation breaks
- Flask's `request.get_json()` can return non-dict JSON (a list, a string) — need `isinstance(body, dict)` check
- `AbortController` + `setTimeout` in JS adds fetch timeouts — without it, a hanging server request blocks the UI forever

### What clicked:
- Empty `allStates.reduce()` without an initialValue crashes if the array is empty — needed a guard before the reduce
- The difference between `err.message` (undefined when `err` is not an Error object) and `err?.message || 'Unknown error'`

### Still confused about:
- When to validate on the frontend vs backend — I now do both, but I'm not sure exactly where each check belongs

### Resources used:
- MDN — AbortController
- OWASP input validation cheat sheet

### Code I wrote today:
```jsx
// Guard against null counts before building chart
const safeCounts = counts || {}
const safeIdeal  = ideal_counts || {}
const safeShots  = shots > 0 ? shots : 1
const allStates = Array.from(
  new Set([...Object.keys(safeCounts), ...Object.keys(safeIdeal)])
).sort()

if (allStates.length === 0) {
  return <section className="results-panel--empty">No measurement data</section>
}
```

### Tomorrow's goals:
- Write pytest tests for all backend modules
- Set up uv properly with pyproject.toml

---

## Day 11 — 2026-03-18
**Phase:** Testing with pytest + uv Setup
**Time spent:** 2 hours
**Commits made:**
- [x] `Add uv, pytest tests, and spec-kit specifications`

### What I learned:
- `uv` is a modern Python package manager — faster than pip, uses `pyproject.toml` instead of `requirements.txt`, generates a `uv.lock` for reproducible installs
- pytest fixtures with `monkeypatch` let you override module-level variables during tests (e.g., swap the database path for a temp file)
- Flask's `test_client()` lets you make HTTP requests to your app without running a real server
- `monkeypatch.setattr()` can mock out expensive functions — I mocked `run_named_circuit` in API tests so they don't actually run Qiskit

### What clicked:
- `[tool.pytest.ini_options] pythonpath = ["backend"]` in pyproject.toml adds `backend/` to the Python path so `import quantum_engine` works in tests without any `sys.path` hacking
- The pyramid: many fast unit tests (noise models, database) + fewer slower integration tests (quantum engine runs) + API tests with mocked simulation

### Still confused about:
- When to use `pytest.fixture(scope="session")` vs default `scope="function"` — I used function scope everywhere which re-creates the DB for every test
- How to test async code in pytest — the sweep logic is async but I didn't write frontend tests

### Resources used:
- pytest docs — fixtures and monkeypatching
- uv docs — pyproject.toml configuration

### Code I wrote today:
```python
@pytest.fixture
def temp_db(monkeypatch, tmp_path):
    db_path = str(tmp_path / 'test_quantum.db')
    import database
    monkeypatch.setattr(database, 'DB_PATH', db_path)
    database.init_db()
    return db_path

def test_bell_ideal_only_00_and_11(self):
    counts = run_named_circuit('bell', 0.0, 512)
    assert set(counts.keys()).issubset({'00', '11'})
```

### Tomorrow's goals:
- Write all 4 spec-kit feature specifications
- Final GitHub cleanup — topics, README, learning log

---

## Day 12 — 2026-03-18
**Phase:** Spec-Kit Specifications + Final Documentation
**Time spent:** 1 hour
**Commits made:**
- [x] `Update README: reflect React/Vite stack, uv, live deploy, tests, and specs`

### What I learned:
- Spec-kit forces you to think about what you're building *before* you build it — user stories, acceptance criteria, technical design
- Writing specs after the fact (like I did here) is still valuable — it documents why decisions were made
- GitHub repository metadata matters: topics/tags help people find your project; a good README is the first impression

### What clicked:
- The four features map cleanly to spec files: quantum engine, noise models, Flask API, noise sweep
- A good README tells you how to run it in under 30 seconds — prerequisites, two commands, done

### Still confused about:
- Spec-kit's `speckit.implement` command — I wrote specs manually, but the tool probably generates more structured output

### Resources used:
- spec-kit repository and README

### Code I wrote today:
```markdown
## Acceptance Criteria
- [ ] Bell State: ideal run produces only `00` and `11` keys in counts dict
- [ ] Grover: ideal run produces `11` with ~100% probability
- [ ] `run_named_circuit` raises `ValueError` for unknown circuit names
```

### Tomorrow's goals:
- Project complete! Submit by 11:30 AM CST.

---

## Day 13 — 2026-03-18
**Phase:** Final Testing + Bug Fixes
**Time spent:** 0.5 hours
**Commits made:**
- [x] All tests passing (89/89)
- [x] Live deployment verified on Railway + Vercel

### What I learned:
- `uv run pytest` is the correct way to run tests in a uv-managed project
- Always verify the live deployment responds before submitting — curl the API directly

### What clicked:
- The full test suite catches regressions — after fixing the error handling issues, tests immediately confirmed nothing else broke

### Still confused about:
- Why the Vercel proxy works (returns 200) but the browser still showed an error — turned out `VITE_API_URL` was still set as an environment variable, overriding the proxy

### Bugs I fixed:
1. `VITE_API_URL` still set in Vercel dashboard → browser bypassed the proxy → CORS blocked → deleted the env var
2. "Moderate" button label clipping on small screens → switched to `clamp()` font sizing
3. `allStates.reduce()` crash on empty array → added early return guard

### Tomorrow's goals:
- Project submitted ✓

---

## Day 14 — 2026-03-18
**Phase:** Project Complete
**Time spent:** 0.5 hours
**Commits made:**
- [x] All commits pushed before 11:30 AM CST deadline

### What I learned:
- Building something from spec to deployed production app teaches you more than any tutorial
- Every layer of the stack has its own "gotcha": Python imports, SQL transactions, CORS, React re-renders, deployment env vars
- Reading error messages carefully is a skill — most bugs told me exactly what was wrong

### What clicked:
- The full architecture: Browser → Vercel proxy → Railway (Flask) → Qiskit → SQLite → back up the chain
- Why AI code assistants are useful for *speed* but you still need to understand the code — I had to debug CORS, port conflicts, and React state issues myself

### Project Complete! Final reflection:

**What I'm most proud of:**
The noise sweep feature — watching the fidelity line chart drop from ~100% at 0% error rate to ~30% at 20% is genuinely satisfying. It's real physics, computed in real time, displayed beautifully.

**What I'd do differently:**
Set up uv and write tests from Day 1 instead of adding them at the end. TDD would have caught the `allStates.reduce()` crash before it ever made it to the deployed app.

**What surprised me about quantum computing:**
How simple the *code* is compared to how mind-bending the *concepts* are. `circuit.h(0)` is three characters but represents a mathematical operation that has no classical equivalent.

**What surprised me about full-stack development:**
How much of the work is plumbing — connecting layers, handling errors at boundaries, configuring CORS, setting up deployment pipelines. The "interesting" code (Qiskit simulation) was maybe 20% of the total work.

**What I want to learn next:**
- Quantum error correction (the real solution to the noise problem we simulated)
- TypeScript for the frontend
- PostgreSQL to replace SQLite in production

**Total hours spent:** ~25 hours across 3 intense sessions

**Would I recommend this project to another CS student? Why?**
Yes — it hits multiple learning goals at once: quantum computing concepts, REST API design, React, database schema, deployment, and testing. The visual feedback (watching the bar chart degrade with noise) makes abstract quantum physics feel real and understandable.

---

## Overall Stats

| Metric | Value |
|---|---|
| Total working sessions | 3 (March 2, March 12, March 18) |
| Total hours | ~25 hours |
| Total commits | 19 |
| Lines of code written | ~6,500 |
| Test cases | 89 (all passing) |
| Bugs squashed | 8+ (CORS, port conflict, button clipping, React key animation, reduce crash, division by zero, fetch timeout, sweep error message) |
| New concepts learned | 15+ (qubits, entanglement, depolarizing noise, Qiskit, AerSimulator, Flask CORS, SQLite transactions, React hooks, Vite proxy, Vercel rewrites, Railway deployment, pytest fixtures, uv, spec-kit, AbortController) |
| Features shipped | 4 (quantum engine, noise models, Flask API, noise sweep) |
