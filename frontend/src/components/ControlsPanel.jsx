/**
 * ControlsPanel.jsx — Simulation Controls
 * =========================================
 * Left sidebar with:
 *   - Circuit selector dropdown (populated from /api/circuits)
 *   - Noise preset quick-pick buttons
 *   - Error rate slider (0.00 – 0.20)
 *   - Shots input (100 – 8192)
 *   - Run Simulation button
 *
 * Props:
 *   circuits     — array from /api/circuits
 *   loading      — bool; disables form while simulation runs
 *   sweepLoading — bool; disables form while sweep is running
 *   loadParams   — {circuit, error_rate, shots} set when user clicks a history
 *                  item; this component syncs its local state to match
 *   onRun        — callback(params) called on form submit
 *   onSweep      — callback(circuit, circuitName) triggers noise sweep
 */

import { useState, useEffect } from 'react'

const CIRCUIT_DESCRIPTIONS = {
  bell:          'Entangles 2 qubits. With no noise, measures only |00⟩ and |11⟩.',
  ghz:           'Entangles 3 qubits. Ideal result: equal mix of |000⟩ and |111⟩.',
  teleportation: "Transfers qubit state using entanglement. Bob's qubit always matches Alice's original state.",
  grover:        'Searches unsorted data. Amplifies the target state |11⟩ above all others.',
}

// Quick preset buttons — let users jump to representative noise levels
// without dragging the slider. Real-world context labels help intuition.
const NOISE_PRESETS = [
  { label: 'Ideal',    value: 0.00, title: 'No noise — perfect quantum computer' },
  { label: 'Low',      value: 0.01, title: '~IBM best hardware (2024)' },
  { label: 'Moderate', value: 0.05, title: 'Errors clearly visible in chart' },
  { label: 'High',     value: 0.10, title: 'Algorithms start failing' },
  { label: 'Extreme',  value: 0.20, title: 'Nearly random results' },
]

export default function ControlsPanel({ circuits, loading, sweepLoading, loadParams, onRun, onSweep }) {
  const [circuit, setCircuit]     = useState('bell')
  const [errorRate, setErrorRate] = useState(0.05)
  const [shots, setShots]         = useState(1024)

  // ── Sync form when a history item is clicked ──────────────────
  // loadParams comes from the parent (App) when the user clicks a
  // history entry. useEffect watches it and updates local state.
  // This is the "controlled from outside" pattern in React.
  useEffect(() => {
    if (!loadParams) return
    setCircuit(loadParams.circuit)
    setErrorRate(loadParams.error_rate)
    setShots(loadParams.shots)
  }, [loadParams])

  const isDisabled = loading || sweepLoading

  function handleSubmit(e) {
    e.preventDefault()
    const clampedShots = Math.max(100, Math.min(8192, shots || 1024))
    onRun({ circuit, error_rate: errorRate, shots: clampedShots })
  }

  function handleSweep() {
    if (!circuits.length) return
    const circuitName = circuits.find(c => c.id === circuit)?.name || circuit
    onSweep(circuit, circuitName)
  }

  function errorRateColor(p) {
    if (p === 0)   return 'var(--color-success)'
    if (p <= 0.01) return 'var(--color-success)'
    if (p <= 0.05) return 'var(--color-warning)'
    if (p <= 0.10) return 'var(--color-danger)'
    return '#ff4444'
  }

  return (
    <aside className="controls-panel">
      <h2 className="panel-title">Simulation Controls</h2>

      <form onSubmit={handleSubmit} className="controls-form">

        {/* ── Circuit Selector ───────────────────────────────────── */}
        <div className="form-group">
          <label htmlFor="circuit-select" className="form-label">
            Quantum Circuit
          </label>
          <select
            id="circuit-select"
            className="form-select"
            value={circuit}
            onChange={e => setCircuit(e.target.value)}
            disabled={isDisabled}
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

        {/* ── Error Rate ─────────────────────────────────────────── */}
        <div className="form-group">
          <label htmlFor="error-rate" className="form-label">
            Error Rate&nbsp;
            <span className="form-value" style={{ color: errorRateColor(errorRate) }}>
              {(errorRate * 100).toFixed(1)}%
            </span>
          </label>

          {/* Preset quick-pick buttons */}
          <div className="noise-presets" role="group" aria-label="Noise presets">
            {NOISE_PRESETS.map(p => (
              <button
                key={p.value}
                type="button"
                className={`preset-btn ${errorRate === p.value ? 'preset-btn--active' : ''}`}
                onClick={() => setErrorRate(p.value)}
                disabled={isDisabled}
                title={p.title}
              >
                {p.label}
              </button>
            ))}
          </div>

          <input
            id="error-rate"
            type="range"
            className="form-range"
            min="0"
            max="0.20"
            step="0.005"
            value={errorRate}
            onChange={e => setErrorRate(parseFloat(e.target.value))}
            disabled={isDisabled}
          />
          <div className="range-labels">
            <span>0% (ideal)</span>
            <span>20% (noisy)</span>
          </div>
        </div>

        {/* ── Shots ──────────────────────────────────────────────── */}
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
            onChange={e => setShots(parseInt(e.target.value, 10) || 1024)}
            disabled={isDisabled}
          />
          <p className="form-hint">
            More shots = more accurate statistics. Range: 100–8192.
          </p>
        </div>

        {/* ── Submit ─────────────────────────────────────────────── */}
        <button
          type="submit"
          className={`btn-run ${loading ? 'btn-run--loading' : ''}`}
          disabled={isDisabled || circuits.length === 0}
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

        {/* ── Noise Sweep ────────────────────────────────────────── */}
        <button
          type="button"
          className={`btn-sweep ${sweepLoading ? 'btn-sweep--loading' : ''}`}
          disabled={isDisabled || circuits.length === 0}
          onClick={handleSweep}
          title="Run 8 simulations across all error rates and plot the fidelity degradation curve"
        >
          {sweepLoading ? (
            <>
              <span className="spinner" aria-hidden="true" />
              Sweeping…
            </>
          ) : (
            <>
              <span aria-hidden="true">📈</span>
              Run Noise Sweep
            </>
          )}
        </button>

      </form>
    </aside>
  )
}
