# API Reference — Quantum Circuit Error Analyzer

## Overview

The backend exposes a JSON REST API over HTTP. All responses are JSON.
The base URL during local development is `http://localhost:5000`.

### What is a REST API?

REST (Representational State Transfer) is a set of conventions for building web APIs.
The key ideas:
- **Resources** are identified by URLs (`/api/circuits`, `/api/simulate`)
- **HTTP methods** say what you want to do (GET = read, POST = create)
- **JSON** is the data format for requests and responses
- **Status codes** signal success (200), client errors (400), server errors (500)

---

## Endpoints Summary

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/circuits` | List all 4 available circuits |
| POST | `/api/simulate` | Run a circuit simulation |
| GET | `/api/results/<id>` | Get a past simulation by ID |
| GET | `/api/history` | Get last 20 simulations |

---

## GET /api/circuits

Returns metadata about all 4 quantum circuits available for simulation.

### Request

```
GET /api/circuits
```

No headers, no body, no parameters needed.

### Response 200 OK

```json
{
  "circuits": [
    {
      "id": "bell",
      "name": "Bell State",
      "description": "Creates a maximally entangled 2-qubit state. The simplest demonstration of quantum entanglement.",
      "num_qubits": 2,
      "difficulty": "beginner"
    },
    {
      "id": "ghz",
      "name": "GHZ State",
      "description": "3-qubit generalized entangled state. All qubits are correlated.",
      "num_qubits": 3,
      "difficulty": "beginner"
    },
    {
      "id": "teleportation",
      "name": "Quantum Teleportation",
      "description": "Transfers a quantum state from one qubit to another using entanglement.",
      "num_qubits": 3,
      "difficulty": "intermediate"
    },
    {
      "id": "grover",
      "name": "Grover's Algorithm",
      "description": "Quantum search algorithm that finds a marked item quadratically faster than classical search.",
      "num_qubits": 2,
      "difficulty": "intermediate"
    }
  ]
}
```

### Response Fields

| Field | Type | Description |
|---|---|---|
| `id` | string | Internal identifier used in simulate requests |
| `name` | string | Human-readable display name |
| `description` | string | One-sentence explanation for UI |
| `num_qubits` | integer | How many qubits this circuit uses |
| `difficulty` | string | `"beginner"` or `"intermediate"` |

### curl Example

```bash
curl http://localhost:5000/api/circuits
```

---

## POST /api/simulate

Runs a quantum circuit simulation with the specified noise level and returns results.

### Request

```
POST /api/simulate
Content-Type: application/json
```

**Body:**
```json
{
  "circuit": "bell",
  "error_rate": 0.05,
  "shots": 1024
}
```

**Request fields:**

| Field | Type | Required | Constraints | Default |
|---|---|---|---|---|
| `circuit` | string | Yes | `bell`, `ghz`, `teleportation`, `grover` | — |
| `error_rate` | float | Yes | `0.0` ≤ value ≤ `0.20` | — |
| `shots` | integer | No | `100` ≤ value ≤ `8192` | `1024` |

**What `shots` means:** The number of times the circuit is executed. More shots = more accurate
statistics but slower simulation. 1024 is a good balance.

**What `error_rate` means:** The depolarizing error probability per gate.
- `0.0` = perfect quantum computer (theoretical ideal)
- `0.05` = 5% chance of error per gate (quite noisy)
- `0.20` = 20% chance of error per gate (extremely noisy)

### Response 200 OK

```json
{
  "simulation_id": 42,
  "circuit": "bell",
  "error_rate": 0.05,
  "shots": 1024,
  "counts": {
    "00": 467,
    "01": 28,
    "10": 22,
    "11": 507
  },
  "ideal_counts": {
    "00": 512,
    "11": 512
  },
  "created_at": "2024-01-15T14:32:00"
}
```

**Response fields:**

| Field | Type | Description |
|---|---|---|
| `simulation_id` | integer | Unique ID — use this for `/api/results/<id>` |
| `circuit` | string | The circuit that was run |
| `error_rate` | float | The noise level used |
| `shots` | integer | Number of runs |
| `counts` | object | Actual measurement results `{state: count}` |
| `ideal_counts` | object | Theoretical perfect results for comparison |
| `created_at` | string | ISO 8601 timestamp |

**Understanding `counts`:**
Each key is a binary string representing the measurement outcome.
For a 2-qubit circuit, possible keys are `"00"`, `"01"`, `"10"`, `"11"`.
For a 3-qubit circuit: `"000"`, `"001"`, ..., `"111"`.
The value is how many times that outcome occurred out of `shots` total.

**Note:** Not all states appear in `counts` — only states that occurred at least once.
States with 0 count are simply absent from the dict.

### Response 400 Bad Request — Missing or invalid field

```json
{
  "error": "circuit is required",
  "code": "MISSING_FIELD"
}
```

```json
{
  "error": "Invalid circuit. Must be one of: ['bell', 'ghz', 'teleportation', 'grover']",
  "code": "INVALID_CIRCUIT"
}
```

### Response 422 Unprocessable Entity — Value out of range

```json
{
  "error": "error_rate must be between 0.0 and 0.20",
  "code": "OUT_OF_RANGE"
}
```

### Response 500 Internal Server Error — Simulation failed

```json
{
  "error": "Simulation failed: [specific error message]",
  "code": "SIMULATION_ERROR"
}
```

### curl Examples

**Basic Bell State at 5% noise:**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "bell", "error_rate": 0.05, "shots": 1024}'
```

**GHZ State with no noise (ideal):**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "ghz", "error_rate": 0.0}'
```

**Grover's at 15% noise, 2048 shots:**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "grover", "error_rate": 0.15, "shots": 2048}'
```

**Invalid circuit (test error handling):**
```bash
curl -X POST http://localhost:5000/api/simulate \
  -H "Content-Type: application/json" \
  -d '{"circuit": "shor", "error_rate": 0.05}'
# Expected: 400 {"error": "Invalid circuit...", "code": "INVALID_CIRCUIT"}
```

---

## GET /api/results/\<id\>

Retrieves a complete past simulation (metadata + measurement results) by its ID.

### Request

```
GET /api/results/42
```

No body needed. The `42` in the URL is the `simulation_id` returned by `/api/simulate`.

### Response 200 OK

```json
{
  "simulation": {
    "id": 42,
    "circuit_id": "bell",
    "circuit_name": "Bell State",
    "error_rate": 0.05,
    "shots": 1024,
    "created_at": "2024-01-15T14:32:00"
  },
  "results": [
    {"state": "00", "count": 467},
    {"state": "01", "count": 28},
    {"state": "10", "count": 22},
    {"state": "11", "count": 507}
  ]
}
```

### Response 404 Not Found

```json
{
  "error": "Simulation 42 not found",
  "code": "NOT_FOUND"
}
```

### curl Examples

```bash
# Get simulation with ID 1
curl http://localhost:5000/api/results/1

# Get simulation with ID 42
curl http://localhost:5000/api/results/42

# Test 404 handling
curl http://localhost:5000/api/results/99999
# Expected: 404 {"error": "Simulation 99999 not found", "code": "NOT_FOUND"}
```

---

## GET /api/history

Returns a list of recent simulations, newest first.

### Request

```
GET /api/history
GET /api/history?limit=5
GET /api/history?circuit=bell
GET /api/history?limit=10&circuit=grover
```

**Query parameters (all optional):**

| Parameter | Type | Default | Description |
|---|---|---|---|
| `limit` | integer | `20` | Max number of results to return |
| `circuit` | string | (none) | Filter by circuit name |

### Response 200 OK

```json
{
  "simulations": [
    {
      "id": 42,
      "circuit_name": "Bell State",
      "error_rate": 0.05,
      "shots": 1024,
      "created_at": "2024-01-15T14:32:00"
    },
    {
      "id": 41,
      "circuit_name": "Grover's Algorithm",
      "error_rate": 0.10,
      "shots": 2048,
      "created_at": "2024-01-15T13:15:00"
    }
  ],
  "total": 2
}
```

### curl Examples

```bash
# Get last 20 simulations
curl http://localhost:5000/api/history

# Get last 5 simulations
curl "http://localhost:5000/api/history?limit=5"

# Get only Bell State simulations
curl "http://localhost:5000/api/history?circuit=bell"
```

---

## HTTP Status Code Reference

| Code | Meaning | When It Happens |
|---|---|---|
| `200` | OK | Request succeeded |
| `400` | Bad Request | Missing field or wrong type in request body |
| `404` | Not Found | Simulation ID doesn't exist in database |
| `422` | Unprocessable Entity | Field exists but value is out of range |
| `500` | Internal Server Error | Qiskit simulation crashed or unexpected error |

---

## JavaScript Fetch Example

How to call the API from `app.js`:

```javascript
async function runSimulation(circuit, errorRate, shots = 1024) {
  try {
    const response = await fetch('http://localhost:5000/api/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        circuit: circuit,
        error_rate: errorRate,
        shots: shots
      })
    });

    if (!response.ok) {
      const err = await response.json();
      throw new Error(err.error);
    }

    const data = await response.json();
    return data;   // { simulation_id, counts, ideal_counts, ... }

  } catch (error) {
    console.error('Simulation failed:', error.message);
    throw error;
  }
}
```
