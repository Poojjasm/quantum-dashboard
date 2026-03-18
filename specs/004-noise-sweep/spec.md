# Feature Spec: Noise Sweep — Fidelity Degradation Curve

**Feature ID**: 004-noise-sweep
**Status**: Implemented

## Overview

Implement a "Noise Sweep" feature that runs a selected quantum circuit at 8 pre-defined error
rates (0%, 0.5%, 1%, 2%, 5%, 10%, 15%, 20%) and plots a fidelity-vs-error-rate line chart.
Fidelity is defined as the fraction of shots that landed on an ideal (expected) quantum state.
The sweep runs sequentially with live progress updates, revealing how noise degrades each circuit.

## User Stories

- As a student, I want to see a fidelity curve so I understand how noise affects quantum algorithms.
- As a user, I want to see live progress (e.g. "3/8 complete") while the sweep runs.
- As a user, I want the sweep to show which circuits (Bell vs Grover) degrade faster under noise.
- As a user, I want the sweep chart to be separate from the single-run bar chart.

## Requirements

1. Sweep runs 8 simulations at rates: `[0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]`.
2. Each sweep point uses 512 shots (fast but statistically meaningful).
3. Fidelity = (shots on ideal states / total shots) × 100.
4. Results are displayed as a line chart (FidelityChart component) with error rate on X axis.
5. `runSweep(circuit, circuitName)` is exposed from `useSimulation` hook.
6. `sweepLoading` and `sweepProgress` (0–8) are exposed for UI progress display.
7. If any sweep point fails (network error, timeout), the sweep stops and shows an error.
8. Each fetch call has a 30-second AbortController timeout.
9. Sweep response is validated: `data.counts`, `data.ideal_counts`, `data.shots` must exist.
10. Error messages use `err?.message || 'Unknown error'` (no "undefined" strings).

## Technical Design

- **Frontend**: `useSimulation.js` → `runSweep()` → 8 sequential `POST /api/simulate` calls
- **Chart**: `FidelityChart.jsx` renders a line chart via Chart.js (react-chartjs-2)
- **Progress**: `sweepProgress` state (0–8) incremented after each successful point
- **Data shape**: `sweepData = { circuit, circuitName, points: [{errorRate, fidelity}] }`

## Acceptance Criteria

- [ ] Clicking "Run Noise Sweep" runs 8 simulations sequentially
- [ ] Progress counter updates after each completed point
- [ ] Fidelity at error_rate=0 is near 100%
- [ ] Fidelity at error_rate=0.20 is visibly lower than at 0
- [ ] A network failure at any point stops the sweep and shows an error message
- [ ] FidelityChart renders a line chart with 8 data points after sweep completes
- [ ] Sweep button is disabled while sweep is in progress
