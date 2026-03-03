# Learning Resources — Quantum Dashboard Project

> All links verified and curated for beginner-to-intermediate level.
> Organized by topic so you can dive deep on exactly what you need.

---

## How to Use This File

- **Stuck on quantum concepts?** → Section 1
- **Stuck on Python/Flask?** → Section 2
- **Stuck on JavaScript?** → Section 3
- **Stuck on databases?** → Section 4
- **Stuck on Git?** → Section 5
- **Want to go deeper after the project?** → Section 6

---

## Section 1: Quantum Computing

### Start Here (Beginner, Free)

**IBM Quantum Learning**
- URL: https://learning.quantum.ibm.com
- What it covers: Free, interactive quantum computing course from IBM
- Why it's great: Hands-on with real quantum hardware, beginner-friendly modules
- Time: 3-5 hours for the basics
- **Recommended:** Start with "Basics of Quantum Information" course

**Qiskit Textbook**
- URL: https://github.com/Qiskit/textbook
- What it covers: The official Qiskit textbook — math, circuits, algorithms
- Why it's great: Interactive Jupyter notebooks, very thorough
- Time: Reference as needed; don't try to read cover to cover

**Qiskit Official Docs**
- URL: https://docs.quantum.ibm.com
- What it covers: Every Qiskit function and class documented
- Why it's great: The ground truth — when something doesn't work, check here
- How to use: Search for specific function names, not a read-through

---

### Videos (Visual Learners)

**Qiskit YouTube Channel**
- URL: https://www.youtube.com/@qiskit
- What it covers: Quantum computing tutorials, Qiskit code walkthroughs
- **Best videos for this project:**
  - "Introduction to Quantum Computing" playlist
  - "What is Quantum Entanglement?"
  - "Grover's Search Algorithm"

**3Blue1Brown — But What is a Quantum Computer?**
- URL: Search "3Blue1Brown quantum computing" on YouTube
- What it covers: Visual, mathematical intuition for superposition and measurement
- Why it's great: The best visual explanation of the math (30 min, no Qiskit)

**Veritasium — How Quantum Computers Could Change Everything**
- URL: Search "Veritasium quantum computers" on YouTube
- What it covers: High-level overview of why quantum computing matters
- Time: 20 minutes — good for the big picture

---

### Go Deeper (After Project)

**"Quantum Computing: An Applied Approach" by Jack Hidary**
- Format: Book (physical/ebook)
- Level: Intermediate
- Covers: Qiskit implementation of major algorithms with math

**Nielsen & Chuang — "Quantum Computation and Quantum Information"**
- Format: Book (free PDF available)
- Level: Advanced (the "bible" of quantum computing)
- Use it: When you're ready for the real math after this project

**IBM Quantum Experience**
- URL: https://quantum.ibm.com
- What it covers: Free access to real IBM quantum computers
- Why it's great: Run your circuits on actual quantum hardware, not just simulation

---

## Section 2: Python & Flask

### Python Refresher

**Python Official Tutorial**
- URL: https://docs.python.org/3/tutorial/
- What it covers: Everything from basics to advanced Python features
- Use it: When you hit a Python syntax question

**Real Python**
- URL: https://realpython.com
- What it covers: Practical Python tutorials with real-world examples
- **Best for this project:**
  - "Python Virtual Environments Primer"
  - "SQLite in Python"
  - "Flask REST APIs"

---

### Flask

**Flask Official Documentation**
- URL: https://flask.palletsprojects.com/en/3.0.x/
- What it covers: Complete Flask reference
- **Key pages:**
  - Quickstart: Your first Flask app
  - Request: How to read request data
  - Routing: URL routing with decorators
  - JSON: Returning JSON responses

**Flask Mega-Tutorial by Miguel Grinberg**
- URL: https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world
- What it covers: Full Flask application from scratch (25 chapters)
- Time: Full tutorial is long — skim chapters 1, 3, and 4 for this project
- Why it's great: Most comprehensive Flask tutorial online

**Flask-CORS Documentation**
- URL: https://flask-cors.readthedocs.io
- What it covers: How to add CORS headers so your browser can call Flask
- Why it matters: Without this, every fetch() from the browser will fail

---

## Section 3: JavaScript & Frontend

### JavaScript Fundamentals

**MDN JavaScript Guide**
- URL: https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide
- What it covers: Complete JavaScript reference from Mozilla
- **Key pages for this project:**
  - "Working with JSON"
  - "Promises" and "async/await"
  - "Fetch API" (making HTTP requests from the browser)

**javascript.info**
- URL: https://javascript.info
- What it covers: Modern JavaScript from basics to advanced
- Why it's great: Well-structured, free, interactive examples
- **Best sections:**
  - "Promises, async/await" (Chapter 11)
  - "Fetch" (under Network requests)
  - "DOM manipulation" (Chapter 1.3)

---

### Async/Await and Fetch API

**MDN — Using Fetch**
- URL: https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API/Using_Fetch
- What it covers: How to make HTTP requests from JavaScript
- Why it matters: This is how app.js calls the Flask API

**Example pattern you'll use:**
```javascript
// This is the pattern for every API call in app.js
async function callAPI() {
  const response = await fetch('/api/simulate', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ circuit: 'bell', error_rate: 0.05 })
  });

  const data = await response.json();
  return data;
}
```

---

### Chart.js

**Chart.js Official Documentation**
- URL: https://www.chartjs.org/docs/latest/
- What it covers: Every chart type, configuration option, and plugin
- **Key pages:**
  - Getting Started
  - Bar Chart
  - Data structures
  - Styling

**Chart.js Samples Gallery**
- URL: https://www.chartjs.org/docs/latest/samples/
- What it covers: Live demos of every chart type
- **Relevant samples:** Bar Chart, Grouped Bar Chart

**Quick start for our project:**
```html
<!-- Add to index.html -->
<canvas id="resultsChart"></canvas>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

```javascript
// In app.js
const ctx = document.getElementById('resultsChart');
new Chart(ctx, {
  type: 'bar',
  data: {
    labels: ['|00⟩', '|01⟩', '|10⟩', '|11⟩'],
    datasets: [{
      label: 'Measurement Count',
      data: [467, 28, 22, 507],
      backgroundColor: 'rgba(99, 102, 241, 0.8)'
    }]
  }
});
```

---

### HTML & CSS

**MDN HTML Guide**
- URL: https://developer.mozilla.org/en-US/docs/Learn/HTML
- Key sections: Forms, semantic elements, accessibility

**MDN CSS Guide**
- URL: https://developer.mozilla.org/en-US/docs/Learn/CSS
- Key sections: Flexbox, Grid, custom properties (variables)

**CSS Tricks — A Complete Guide to Flexbox**
- URL: https://css-tricks.com/snippets/css/a-guide-to-flexbox/
- A visual, practical guide to CSS Flexbox layout

**CSS Tricks — A Complete Guide to Grid**
- URL: https://css-tricks.com/snippets/css/complete-guide-grid/
- For building the dashboard two-column layout

---

## Section 4: Databases

### SQLite

**SQLite Official Documentation**
- URL: https://www.sqlite.org/docs.html
- What it covers: Complete SQLite reference
- Use it: When you hit SQL questions about SQLite-specific behavior

**Python sqlite3 Module Docs**
- URL: https://docs.python.org/3/library/sqlite3.html
- What it covers: How to use SQLite from Python
- **Key sections:**
  - Connection and cursor basics
  - Parameterized queries (always use these to prevent SQL injection!)
  - Row factory for dict-like rows

**SQLBolt — Interactive SQL Tutorial**
- URL: https://sqlbolt.com
- What it covers: SQL from beginner to advanced with interactive exercises
- Why it's great: Hands-on practice in the browser
- Time: Complete Lessons 1-12 (about 2 hours) for solid SQL fundamentals

---

### Database Design

**Database Design Tutorial (Lucidchart)**
- URL: Search "Lucidchart database design tutorial" on YouTube
- What it covers: How to design tables, relationships, and schemas
- Why it matters: Good schema design prevents bugs and makes queries easier

**Normalization Explained Simply**
- URL: Search "database normalization explained simply" on YouTube
- What it covers: What 1NF, 2NF, 3NF mean and why they matter

---

## Section 5: Git & GitHub

### Getting Started

**GitHub Official Docs — Getting Started**
- URL: https://docs.github.com/en/get-started
- What it covers: Creating repos, cloning, basic commands

**Git Documentation**
- URL: https://git-scm.com/doc
- What it covers: Every git command explained
- Use it: Reference when something goes wrong

**Interactive Git Tutorial**
- URL: https://learngitbranching.js.org
- What it covers: Visual, interactive git branching tutorial
- Time: 1-2 hours, completely worth it

---

### Commit Message Conventions

We use **Conventional Commits** for this project:

```
<type>: <short description>

Types:
  feat:     New feature
  fix:      Bug fix
  docs:     Documentation only
  chore:    Maintenance, tooling, config
  test:     Adding or updating tests
  style:    CSS changes, formatting (no logic changes)
  refactor: Code reorganization (no new features or bug fixes)

Examples:
  feat: implement Bell State circuit with Qiskit
  feat: add depolarizing noise model
  fix: correct CNOT gate qubit order in GHZ circuit
  docs: add API documentation
  chore: add .gitignore and requirements.txt
  test: add unit tests for quantum engine
```

**Why conventional commits?**
- Makes your commit history readable at a glance
- Industry standard — used at Google, Microsoft, and thousands of open source projects
- Required for automatic changelog generation tools

---

## Section 6: Going Deeper (After the Project)

### Quantum Computing — Next Level

**Qiskit Algorithms Library**
- URL: https://qiskit-community.github.io/qiskit-algorithms/
- After this project: Implement Shor's algorithm, QAOA, VQE

**Quantum Error Correction (QEC)**
- Search: "Stabilizer codes quantum error correction Qiskit"
- The next frontier: How to protect quantum computations from errors

**Quantum Machine Learning**
- Qiskit Machine Learning: https://qiskit-community.github.io/qiskit-machine-learning/
- Growing field: Use quantum circuits for ML

---

### Full-Stack Web Development — Next Level

**FastAPI** (Flask's modern alternative)
- URL: https://fastapi.tiangolo.com
- Better than Flask: Automatic API docs, type hints, async support

**PostgreSQL** (SQLite's production replacement)
- URL: https://www.postgresql.org/docs/
- When you need: Multiple users, high traffic, advanced SQL features

**React** (if you liked the JS frontend)
- URL: https://react.dev
- For bigger frontends: Component-based UI, massive ecosystem

---

## Quick Reference: Where to Look When Stuck

| Problem | Resource |
|---|---|
| Qiskit function doesn't work | https://docs.quantum.ibm.com |
| Python syntax question | https://docs.python.org/3 |
| Flask route not working | https://flask.palletsprojects.com |
| SQL query question | https://sqlbolt.com |
| JavaScript async confusion | https://javascript.info (Chapter 11) |
| CSS layout broken | https://css-tricks.com/snippets/css/a-guide-to-flexbox/ |
| Chart.js not rendering | https://www.chartjs.org/docs/latest/ |
| Git command forgotten | https://git-scm.com/doc |
