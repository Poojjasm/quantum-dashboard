# Project Setup Guide — Getting Started from Zero

> Follow these steps in order on Day 1.
> Every command is written to run in your Terminal (macOS) or Command Prompt (Windows).

---

## Prerequisites

Before starting, verify you have these installed:

### Python 3.11+
```bash
python3 --version
# Should print: Python 3.11.x or 3.12.x
```

If not installed: Download from https://www.python.org/downloads/
Choose the latest Python 3.11+ release for your OS.

### Git
```bash
git --version
# Should print: git version 2.x.x
```

If not installed:
- macOS: `xcode-select --install` (installs Xcode Command Line Tools including Git)
- Windows: https://git-scm.com/download/win

### A Code Editor
VS Code is recommended: https://code.visualstudio.com
Install the Python extension after opening VS Code.

---

## Step 1: Open the Project

The project already exists at:
```
/Users/poojasmenoena/quantum-dashboard/
```

Open it in your terminal:
```bash
cd /Users/poojasmenoena/quantum-dashboard
ls
# Should show: backend/ frontend/ docs/ tests/ data/ README.md requirements.txt etc.
```

Open in VS Code:
```bash
code .
```

---

## Step 2: Create a Virtual Environment

A virtual environment is a **sandboxed Python installation** for this project only.
It keeps your Qiskit, Flask, etc. separate from system Python.

**Think of it like:** Each project has its own toolbox. You don't mix the tools from different projects.

```bash
# Make sure you're in the project directory
cd /Users/poojasmenoena/quantum-dashboard

# Create the virtual environment
python3 -m venv venv

# You'll see a new venv/ folder created
ls
# backend/ docs/ frontend/ tests/ venv/ .gitignore README.md ...
```

**Activate the virtual environment:**

```bash
# macOS / Linux
source venv/bin/activate

# Windows (Command Prompt)
venv\Scripts\activate.bat

# Windows (PowerShell)
venv\Scripts\Activate.ps1
```

**After activating, your prompt changes:**
```
# Before: your-computer:quantum-dashboard username$
# After:  (venv) your-computer:quantum-dashboard username$
#          ↑ This shows venv is active
```

**Important:** You must activate the virtual environment every time you open a new terminal.
This is the #1 cause of "ImportError: No module named qiskit" — you forgot to activate.

---

## Step 3: Install Dependencies

With the virtual environment activated:

```bash
pip install -r requirements.txt
```

This installs everything in `requirements.txt`:
- Qiskit (quantum circuit builder)
- Qiskit-Aer (quantum simulator)
- Flask (web framework)
- Flask-CORS (allow browser to call API)
- python-dotenv (environment configuration)

**Verify installation:**
```bash
python3 -c "import qiskit; print('Qiskit:', qiskit.__version__)"
python3 -c "from qiskit_aer import AerSimulator; print('Aer: ok')"
python3 -c "import flask; print('Flask:', flask.__version__)"
```

All three should print version numbers without errors.

---

## Step 4: Verify Qiskit Works

Run a tiny test to confirm quantum simulation works:

```bash
python3 -c "
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

circuit = QuantumCircuit(2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure_all()

sim = AerSimulator()
job = sim.run(transpile(circuit, sim), shots=1024)
counts = job.result().get_counts()
print('Bell State test:', counts)
# Should print something like: Bell State test: {'11': 514, '00': 510}
"
```

If this works, Qiskit is correctly installed.

---

## Step 5: Initialize the Database

The SQLite database file will be created automatically when you first run the app.
But you can also create it manually to verify:

```bash
python3 -c "
import sys
sys.path.insert(0, 'backend')
from database import init_db
init_db()
print('Database initialized successfully')
import os
print('DB file created:', os.path.exists('data/quantum_circuits.db'))
"
```

---

## Step 6: Run the Backend

```bash
python3 backend/app.py
```

You should see:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
 * Press CTRL+C to quit
```

**Test it's working** (open a new terminal window, keep the first one running Flask):
```bash
curl http://localhost:5000/api/circuits
# Should return JSON with 4 circuit definitions
```

---

## Step 7: Open the Frontend

Once Flask is running, open the frontend in your browser:

**Option A:** Open the HTML file directly:
```bash
open frontend/index.html      # macOS
# OR
start frontend/index.html     # Windows
```

**Option B:** Have Flask serve the frontend too (later in the project).

**Note:** The fetch() calls in app.js call `http://localhost:5000/api/...`, so Flask must
be running in the background whenever you test the frontend.

---

## Day 1 Checklist

Complete these before starting Phase 1 coding:

- [ ] `python3 --version` shows Python 3.11+
- [ ] `git --version` shows git is installed
- [ ] `cd /Users/poojasmenoena/quantum-dashboard` works
- [ ] `ls` shows the project structure
- [ ] `source venv/bin/activate` shows `(venv)` in prompt
- [ ] `pip install -r requirements.txt` completes without errors
- [ ] Qiskit Bell State test prints `{'00': ~512, '11': ~512}`
- [ ] `python3 backend/app.py` starts without errors
- [ ] `curl http://localhost:5000/api/circuits` returns JSON

If all 9 items are checked, you're ready to build!

---

## Common Problems and Fixes

### "python3: command not found"
- macOS: `brew install python3` or download from python.org
- Windows: Ensure Python was added to PATH during installation. Reinstall and check "Add to PATH"

### "No module named qiskit"
**Cause:** Virtual environment is not activated.
**Fix:**
```bash
source venv/bin/activate    # macOS/Linux
venv\Scripts\activate.bat   # Windows
# Now try again
```

### "Address already in use" when starting Flask
**Cause:** Flask is already running on port 5000 (maybe in another terminal).
**Fix:**
```bash
# Find what's using port 5000
lsof -i :5000           # macOS/Linux

# Kill it (replace XXXX with the PID from the command above)
kill XXXX

# Or just use a different port
python3 backend/app.py --port 5001
```

### pip install fails with permission error
**Cause:** Trying to install globally without the virtual environment.
**Fix:** Activate the virtual environment first, then pip install.
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### "CORS error" in browser console
**Cause:** Flask doesn't have CORS enabled, or Flask isn't running.
**Fix:**
1. Make sure `flask-cors` is installed: `pip install flask-cors`
2. Make sure `CORS(app)` is in `app.py`
3. Make sure Flask is actually running before opening the browser

### "OperationalError: no such table: simulations"
**Cause:** `init_db()` was not called, so tables don't exist yet.
**Fix:** Make sure `app.py` calls `init_db()` at startup:
```python
# Should be near the top of app.py, after importing database
init_db()
```

### Qiskit simulation is very slow
**Cause:** Too many shots, or complex circuit.
**Fix:** Reduce shots in the request: `"shots": 256` instead of 1024.

### Git commits fail with "Author identity unknown"
**Cause:** Git doesn't know your name/email.
**Fix:**
```bash
git config --global user.name "Your Name"
git config --global user.email "your@email.com"
```

---

## VS Code Recommended Extensions

Install these to make development easier:

1. **Python** (by Microsoft) — Python language support, linting, IntelliSense
2. **Pylance** — Better Python IntelliSense
3. **GitLens** — See git history inline in your code
4. **REST Client** — Test API endpoints directly from VS Code (alternative to curl)
5. **SQLite Viewer** — Browse SQLite database files visually

Install via VS Code: `Cmd+Shift+X` (macOS) → search extension name → Install

---

## Project Git Workflow

### Every work session
```bash
# 1. Navigate to project
cd /Users/poojasmenoena/quantum-dashboard

# 2. Activate virtual environment
source venv/bin/activate

# 3. Check what's changed since your last session
git status
git diff

# 4. Do your work...

# 5. Commit when you finish a meaningful chunk
git add backend/quantum_engine.py
git commit -m "feat: implement Bell State circuit"

# 6. Push to GitHub
git push origin main
```

### Commit frequently
Aim for at least 1-2 commits per work session. Small, frequent commits are better than
one huge commit at the end of the week. If something breaks, you can always go back.

```bash
# See your commit history
git log --oneline

# See what changed in a specific commit
git show abc1234
```
