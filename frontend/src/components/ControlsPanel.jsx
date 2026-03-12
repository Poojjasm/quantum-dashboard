/**
 * ControlsPanel.jsx — Simulation Controls
 * =========================================
 * Left sidebar with:
 *   - Circuit selector dropdown (populated from /api/circuits)
 *   - Error rate slider (0.00 – 0.20)
 *   - Shots input (100 – 8192)
 *   - Run Simulation button
 */

import { useState } from 'react'

// Map circuit id → description shown below the dropdown
const CIRCUIT_DESCRIPTIONS = {
  bell: 'Entangles 2 qubits. With no noise, measures only |00⟩ and |11⟩.',
  ghz: 'Entangles 3 qubits. Ideal result: equal mix of |000⟩ and |111⟩.',
  teleportation: 'Transfers qubit state using entanglement. Bob\'s qubit always matches Alice\'s original state.',
  grover: 'Searches unsorted data. Amplifies the target state |11⟩ above all others.',
}

export default function ControlsPanel({ circuits, loading, onRun }) {
  const [circuit, setCircuit]       = useState('bell')
  const [errorRate, setErrorRate]   = useState(0.05)
  const [shots, setShots]           = useState(1024)

  function handleSubmit(e) {
    e.preventDefault()
    onRun({ circuit, error_rate: errorRate, shots })
  }

  // Color the error rate label based on severity
  function errorRateColor(p) {
    if (p === 0)    return 'var(--color-success)'
    if (p <= 0.01)  return 'var(--color-success)'
    if (p <= 0.05)  return 'var(--color-warning)'
    if (p <= 0.10)  return 'var(--color-danger)'
    return '#ff4444'
  }

  return (
    <aside className="controls-panel">
      <h2 className="panel-title">Simulation Controls</h2>

      <form onSubmit={handleSubmit} className="controls-form">

        {/* ── Circuit Selector ─────────────────────────────────── */}
        <div className="form-group">
          <label htmlFor="circuit-select" className="form-label">
            Quantum Circuit
          </label>
          <select
            id="circuit-select"
            className="form-select"
            value={circuit}
            onChange={e => setCircuit(e.target.value)}
            disabled={loading}
          >
            {circuits.length === 0 ? (
              <option value="">Loading…</option>
            ) : (
              circuits.map(c => (
                <option key={c.id} value={c.id}>
                  {c.name} ({c.num_qubits} qubits)
                </option>
              ))
            )}
          </select>
          {circuit && (
            <p className="form-hint">{CIRCUIT_DESCRIPTIONS[circuit]}</p>
          )}
        </div>

        {/* ── Error Rate Slider ───────────────────────────────── */}
        <div className="form-group">
          <label htmlFor="error-rate" className="form-label">
            Error Rate&nbsp;
            <span
              className="form-value"
              style={{ color: errorRateColor(errorRate) }}
            >
              {(errorRate * 100).toFixed(1)}%
            </span>
          </label>
          <input
            id="error-rate"
            type="range"
            className="form-range"
            min="0"
            max="0.20"
            step="0.005"
            value={errorRate}
            onChange={e => setErrorRate(parseFloat(e.target.value))}
            disabled={loading}
          />
          <div className="range-labels">
            <span>0% (ideal)</span>
            <span>20% (noisy)</span>
          </div>
        </div>

        {/* ── Shots Input ─────────────────────────────────────── */}
        <div className="form-group">
          <label htmlFor="shots" className="form-label">
            Shots (measurements)
          </label>
          <input
            id="shots"
            type="number"
            className="form-input"
            min="100"
            max="8192"
            step="128"
            value={shots}
            onChange={e => setShots(parseInt(e.target.value, 10))}
            disabled={loading}
          />
          <p className="form-hint">
            More shots = more accurate statistics. Range: 100–8192.
          </p>
        </div>

        {/* ── Submit ──────────────────────────────────────────── */}
        <button
          type="submit"
          className={`btn-run ${loading ? 'btn-run--loading' : ''}`}
          disabled={loading || circuits.length === 0}
        >
          {loading ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Simulating…
            </>
          ) : (
            'Run Simulation'
          )}
        </button>

      </form>
    </aside>
  )
}
