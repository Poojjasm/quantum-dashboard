# Quantum Computing Concepts — Reference Guide

> **Read this before writing any Qiskit code.**
> Come back to this file whenever something in the code feels confusing.
> The answer is usually here.

---

## Part 1: Classical vs Quantum Computing

### Classical Bits

Every computer you've ever used works with **bits** — tiny transistors that are either OFF (0) or ON (1).
Your phone has billions of them. They follow strict, deterministic rules:

```
AND gate: 1 AND 1 = 1, 1 AND 0 = 0
OR gate:  1 OR  0 = 1, 0 OR  0 = 0
NOT gate: NOT 0  = 1, NOT 1  = 0
```

The bit is ALWAYS exactly 0 or 1. No ambiguity. Very reliable.

### Qubits

A **qubit** (quantum bit) is the quantum version of a bit. Here's the game-changer:
**a qubit can be 0, 1, or both at the same time — until you look at it.**

This is **superposition** and it's the foundation of everything quantum.

---

## Part 2: Superposition

**Analogy:** Spin a coin. While it's spinning, it's neither heads nor tails — it's *in superposition* of both possibilities. When it lands (when you "measure" it), it randomly becomes one or the other.

A qubit in superposition has:
- A probability of being measured as **0**
- A probability of being measured as **1**
- These probabilities must add up to **100%**

The math (you don't need to memorize this, just read it once):
```
|ψ⟩ = α|0⟩ + β|1⟩

Where:
  |0⟩ = state zero (like "heads")
  |1⟩ = state one  (like "tails")
  α   = amplitude for 0 (complex number)
  β   = amplitude for 1 (complex number)
  |α|² + |β|² = 1  (probabilities must sum to 1)
```

**Equal superposition** (50/50 split):
```
|ψ⟩ = (1/√2)|0⟩ + (1/√2)|1⟩
     → 50% chance of measuring 0
     → 50% chance of measuring 1
```

**Why this matters for our project:**
The Bell State circuit creates exactly this — a perfect 50/50 superposition shared between two qubits.
Without noise, you get ~512 "00" and ~512 "11" out of 1024 shots. With noise, you start seeing "01" and "10".

---

## Part 3: Entanglement

**Analogy:** Imagine two magic coins. You flip them in separate rooms — or separate cities, or planets.
Whenever coin A lands heads, coin B *always* lands tails. Instantly. Every time. With no signal passing between them.

This is quantum entanglement. Two (or more) qubits become linked so that measuring one instantly
determines the state of the other, no matter how far apart they are.

Einstein called it "spooky action at a distance" — he was skeptical, but it's been experimentally proven.

**Key properties of entanglement:**
- Measuring one entangled qubit instantly determines the other's state
- The correlation is not due to pre-agreed "hidden information" — it's genuinely random until measured
- Entanglement is *created* by applying CNOT gates after putting a qubit in superposition

**Why this matters for our project:**
- Bell State: 2 entangled qubits
- GHZ State: 3 entangled qubits
- Quantum Teleportation: uses entanglement as a communication channel

---

## Part 4: Quantum Gates

Just like classical computers use logic gates (AND, OR, NOT), quantum computers use **quantum gates**.

Key differences from classical gates:
1. **Quantum gates are reversible** — you can always undo them (unlike AND/OR which lose information)
2. **They rotate qubits** in a mathematical space called the Bloch sphere
3. **They operate on superpositions**, not just 0s and 1s
4. **They're represented as matrices** (the math under the hood)

### Gates We Use in This Project

---

#### Hadamard Gate (H) — The Superposition Creator

Takes a definite state (|0⟩ or |1⟩) and puts it into **equal superposition**.
This is how we start almost every quantum algorithm.

```
H|0⟩ = (|0⟩ + |1⟩) / √2    →  50% chance 0, 50% chance 1
H|1⟩ = (|0⟩ - |1⟩) / √2    →  50% chance 0, 50% chance 1 (different phase)
```

In Qiskit:
```python
circuit.h(0)  # Apply H gate to qubit 0
```

**Think of it as:** A "coin flip" gate — it puts the qubit into a random state.

---

#### Pauli-X Gate (X) — The Quantum NOT

The quantum equivalent of a classical NOT gate. Flips |0⟩ to |1⟩ and vice versa.

```
X|0⟩ = |1⟩
X|1⟩ = |0⟩
```

In Qiskit:
```python
circuit.x(0)  # Apply X gate to qubit 0
```

---

#### CNOT Gate (CX) — The Entangler

A **2-qubit gate** and the most important gate for creating entanglement.
- Takes a **control** qubit and a **target** qubit
- If control = |1⟩ → flip the target
- If control = |0⟩ → do nothing to the target

```
CNOT|00⟩ = |00⟩   (control=0, no flip)
CNOT|01⟩ = |01⟩   (control=0, no flip)
CNOT|10⟩ = |11⟩   (control=1, target flipped: 0→1)
CNOT|11⟩ = |10⟩   (control=1, target flipped: 1→0)
```

In Qiskit:
```python
circuit.cx(0, 1)  # qubit 0 = control, qubit 1 = target
```

**Why H + CNOT creates entanglement:**
```
Start:          |00⟩
After H on q0:  (|0⟩ + |1⟩)/√2 ⊗ |0⟩  =  (|00⟩ + |10⟩) / √2
After CNOT:     (|00⟩ + |11⟩) / √2
```
Now q0 and q1 are correlated — if q0=0 then q1=0, if q0=1 then q1=1. That's entanglement!

---

#### CZ Gate (Controlled-Z) — Phase Flipper

Similar to CNOT but applies a **phase flip** to the target qubit instead of a bit flip.
Used in Grover's algorithm to mark the target state.

```
CZ|11⟩ = -|11⟩   (phase flipped — the negative sign is the "mark")
CZ|00⟩ = |00⟩    (no change)
CZ|01⟩ = |01⟩    (no change)
CZ|10⟩ = |10⟩    (no change)
```

In Qiskit:
```python
circuit.cz(0, 1)
```

---

## Part 5: The 4 Circuits We're Building

---

### Circuit 1: Bell State

**Difficulty:** Beginner | **Qubits:** 2 | **Gates:** H, CNOT
**Named after:** John Bell, who proved entanglement is real (1964)

**What it demonstrates:** The simplest quantum entanglement. The "Hello World" of quantum computing.

**Circuit diagram:**
```
q0: ── H ── ●──  measure
            │
q1: ─────── X──  measure
```

**Step by step:**
1. Start: both qubits in |0⟩
2. Apply H to q0: q0 enters superposition → system is (|00⟩ + |10⟩)/√2
3. Apply CNOT (control=q0, target=q1): entangles them → (|00⟩ + |11⟩)/√2
4. Measure both

**Ideal results (no noise, 1024 shots):**
```
|00⟩ : ~512 counts (50%)
|11⟩ : ~512 counts (50%)
|01⟩ : 0 counts
|10⟩ : 0 counts
```

**With noise:** "01" and "10" appear. More noise = more wrong answers. This is what we visualize!

---

### Circuit 2: GHZ State

**Difficulty:** Beginner | **Qubits:** 3 | **Gates:** H, CNOT, CNOT
**Named after:** Greenberger, Horne, Zeilinger (1989)

**What it demonstrates:** Entanglement across 3 qubits. Often used in quantum error correction research.

**Circuit diagram:**
```
q0: ── H ── ●────────  measure
            │
q1: ─────── X ── ●──  measure
                 │
q2: ──────────── X──  measure
```

**Step by step:**
1. Apply H to q0: puts q0 in superposition
2. CNOT(q0→q1): entangles q0 and q1
3. CNOT(q1→q2): extends entanglement to q2
4. Measure all three

**Ideal results:**
```
|000⟩ : ~512 counts (50%)
|111⟩ : ~512 counts (50%)
Everything else: 0
```

---

### Circuit 3: Quantum Teleportation

**Difficulty:** Intermediate | **Qubits:** 3 | **Gates:** H, CNOT, X, Z
**Note:** Not teleportation of matter — teleportation of *quantum information*

**What it demonstrates:** Transferring a quantum state from one qubit to another using entanglement.
The original state is destroyed in the process (no-cloning theorem).

**The setup:**
- q0 = the "message" qubit (holds the state we want to send)
- q1 = Alice's half of an entangled pair
- q2 = Bob's half of an entangled pair

**Step by step:**
1. Create entangled pair between q1 and q2 (Bell State)
2. Alice entangles her message qubit (q0) with her half of the pair (q1)
3. Alice measures q0 and q1 (gets 2 classical bits)
4. Alice sends those 2 classical bits to Bob (classical communication!)
5. Bob applies corrections to q2 based on those bits
6. Bob's q2 now has the original message state

**Why it's cool:** The quantum state was "teleported" without physically moving the qubit.
The entanglement acts as a quantum communication channel.

**Ideal results:** q2 ends up in the same state q0 started in.

---

### Circuit 4: Grover's Algorithm

**Difficulty:** Intermediate | **Qubits:** 2 | **Gates:** H, X, CZ, H (multiple times)
**Named after:** Lov Grover (1996)

**What it demonstrates:** Quantum speedup for searching.

**The problem:** Find one marked item in a list of 4 items (2 qubits = 4 possible states: 00, 01, 10, 11).

**Classical approach:** Check 1, check 2, check 3 — found it (on average 2.5 checks for 4 items).
**Grover's approach:** 1 iteration and you're done (for 4 items, √4 = 2, but just 1 is enough here).

**How it works (intuition):**
1. Start all states in equal superposition (each has 25% probability)
2. **Oracle:** "Mark" the target state by flipping its phase (makes it slightly negative)
3. **Diffuser:** Reflect all amplitudes around their average — the marked state's probability jumps to ~100%
4. Measure → you get the marked state with high probability

**Circuit diagram (marking state |11⟩):**
```
q0: ── H ── X ── ● ── X ── H ── X ── ● ── X ── H ──  measure
                 │                    │
q1: ── H ── X ── Z ── X ── H ── X ── Z ── X ── H ──  measure
```

**Ideal results (marking |11⟩):**
```
|11⟩ : ~976 counts (~95%)
|00⟩ : ~16 counts  (~1.5%)
|01⟩ : ~16 counts  (~1.5%)
|10⟩ : ~16 counts  (~1.5%)
```

**With noise:** The probability of finding the correct state drops. High error rates make Grover's essentially useless.

---

## Part 6: Quantum Errors and Noise

### Why Quantum Computers Make Errors

Real quantum computers are **extremely sensitive**. Qubits interact with their environment
(heat, electromagnetic fields, vibrations, cosmic rays) and lose their quantum properties.
This process is called **decoherence**.

**Analogy:** Maintaining a qubit's quantum state is like trying to keep a soap bubble perfectly round
in a room full of wind. The slightest disturbance and it pops.

Modern quantum computers (2024) have error rates of roughly 0.1% to 1% per gate.
Our slider goes up to 20% to make the effect dramatically visible.

---

### Types of Quantum Errors

**Bit Flip Error (X error):**
```
|0⟩ → |1⟩  (qubit randomly flips, like a cosmic ray hit)
|1⟩ → |0⟩
```
This IS the quantum analog of a classical bit error.

**Phase Flip Error (Z error):**
```
|+⟩ → |−⟩  (the phase of superposition flips)
(|0⟩ + |1⟩)/√2 → (|0⟩ - |1⟩)/√2
```
No classical equivalent. The qubit looks the same when measured, but quantum interference breaks.

**Depolarizing Error (our model):**
The qubit is randomly replaced by a completely random state.
This is a combination of X, Y, and Z errors happening randomly.

```
With probability (1 - p):  gate works perfectly
With probability p/3:      X error is applied
With probability p/3:      Y error is applied  (Y = bit flip + phase flip)
With probability p/3:      Z error is applied
```

---

### The Depolarizing Noise Model in Our Project

The slider in our UI controls `p` — the probability of an error on each gate.

| Error Rate | Real-world equivalent |
|---|---|
| p = 0.001 (0.1%) | Better than today's best quantum computers |
| p = 0.01 (1%) | About what IBM's best machines achieve (2024) |
| p = 0.05 (5%) | Noticeably noisy — algorithms start failing |
| p = 0.10 (10%) | Heavily degraded — results near random |
| p = 0.20 (20%) | Barely functional — noise dominates |

In Qiskit code:
```python
from qiskit_aer.noise import NoiseModel, depolarizing_error

noise_model = NoiseModel()
error = depolarizing_error(p, 1)          # 1-qubit gate error
error_2 = depolarizing_error(p, 2)        # 2-qubit gate error (usually worse)

noise_model.add_all_qubit_quantum_error(error, ['h', 'x'])   # single-qubit gates
noise_model.add_all_qubit_quantum_error(error_2, ['cx'])      # two-qubit gates
```

---

## Part 7: Why This Matters — The Big Picture

### The NISQ Era

We're currently in the "Noisy Intermediate-Scale Quantum" (NISQ) era.
Quantum computers exist and can run small circuits, but they're too noisy for most useful applications.

The gap between what quantum computers can theoretically do and what they can actually do today
is *exactly* the error we visualize in our dashboard.

### Quantum Error Correction (QEC)

Scientists are actively building quantum error-correcting codes — ways to detect and fix errors
without measuring (which would collapse) the quantum state.

Think of it like:
- Classical: TCP/IP packets have checksums to detect corruption
- Quantum: You need to detect errors without looking at (measuring) the data

Achieving fault-tolerant quantum computing is one of the biggest open problems in physics.

### Why Our Dashboard Matters

Our project visualizes the core challenge of quantum computing in an accessible way.
That gap between the blue "ideal" bars and the orange "noisy" bars in our chart?
That's what $1+ billion in quantum research is working to close.

---

## Quantum Notation Cheat Sheet

| Symbol | Meaning | Pronunciation |
|---|---|---|
| `\|0⟩` | Qubit in state 0 | "ket zero" |
| `\|1⟩` | Qubit in state 1 | "ket one" |
| `\|ψ⟩` | General qubit state | "ket psi" |
| `\|00⟩` | 2-qubit state, both zero | "ket zero zero" |
| `α, β` | Complex amplitudes | "alpha, beta" |
| `\|α\|²` | Probability of measuring 0 | "magnitude squared" |
| `H` | Hadamard gate | |
| `X` | Pauli-X (NOT) gate | |
| `CNOT / CX` | Controlled-NOT gate | |
| `p` | Error probability | |
| `shots` | Number of simulation runs | |
