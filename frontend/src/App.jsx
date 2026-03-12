/**
 * App.jsx — Root Component
 * =========================
 * Layout:
 *   ┌──────────────────────────────────────────────────┐
 *   │  Header                                          │
 *   ├──────────────┬───────────────────────────────────┤
 *   │ ControlsPanel│ ResultsPanel                      │
 *   ├──────────────┴───────────────────────────────────┤
 *   │  HistoryPanel                                    │
 *   └──────────────────────────────────────────────────┘
 *
 * All data fetching lives in useSimulation() hook.
 * Components receive only the slices of state they need.
 */

import './App.css'
import { useSimulation } from './hooks/useSimulation'
import ControlsPanel from './components/ControlsPanel'
import ResultsPanel  from './components/ResultsPanel'
import HistoryPanel  from './components/HistoryPanel'

export default function App() {
  const {
    circuits,
    result,
    history,
    loading,
    error,
    runSimulation,
    clearError,
  } = useSimulation()

  return (
    <div className="app">

      {/* ── Header ─────────────────────────────────────────────── */}
      <header className="app-header">
        <div className="app-header__inner">
          <div className="app-header__brand">
            <span className="app-header__icon" aria-hidden="true">⚛</span>
            <div>
              <h1 className="app-header__title">Quantum Circuit Error Analyzer</h1>
              <p className="app-header__subtitle">
                Simulate depolarizing noise on real quantum algorithms
              </p>
            </div>
          </div>
          <div className="app-header__badges">
            <span className="tech-badge">Qiskit 2.x</span>
            <span className="tech-badge">Flask</span>
            <span className="tech-badge">React</span>
          </div>
        </div>
      </header>

      {/* ── Error Banner ────────────────────────────────────────── */}
      {error && (
        <div className="error-banner" role="alert">
          <span>{error}</span>
          <button
            className="error-banner__close"
            onClick={clearError}
            aria-label="Dismiss error"
          >
            ✕
          </button>
        </div>
      )}

      {/* ── Main Content ───────────────────────────────────────── */}
      <main className="app-main">
        <ControlsPanel
          circuits={circuits}
          loading={loading}
          onRun={runSimulation}
        />
        <ResultsPanel result={result} />
      </main>

      {/* ── History ─────────────────────────────────────────────── */}
      <HistoryPanel history={history} />

    </div>
  )
}
