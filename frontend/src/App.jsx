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
import { useEffect } from 'react'
import { useSimulation } from './hooks/useSimulation'
import ControlsPanel  from './components/ControlsPanel'
import ResultsPanel   from './components/ResultsPanel'
import FidelityChart  from './components/FidelityChart'
import HistoryPanel   from './components/HistoryPanel'

export default function App() {
  // ── Cursor halo effect ─────────────────────────────────────────
  useEffect(() => {
    const inner = document.createElement('div')
    const outer = document.createElement('div')
    inner.className = 'cursor-halo cursor-halo--inner'
    outer.className = 'cursor-halo cursor-halo--outer'
    document.body.appendChild(outer)
    document.body.appendChild(inner)

    let mx = window.innerWidth / 2
    let my = window.innerHeight / 2
    let ix = mx, iy = my
    let ox = mx, oy = my
    let rafId

    const onMove = (e) => { mx = e.clientX; my = e.clientY }
    document.addEventListener('mousemove', onMove)

    const loop = () => {
      ix += (mx - ix) * 0.22
      iy += (my - iy) * 0.22
      ox += (mx - ox) * 0.07
      oy += (my - oy) * 0.07
      inner.style.transform = `translate(${ix}px,${iy}px) translate(-50%,-50%)`
      outer.style.transform = `translate(${ox}px,${oy}px) translate(-50%,-50%)`
      rafId = requestAnimationFrame(loop)
    }
    rafId = requestAnimationFrame(loop)

    const INTERACTIVE = 'button, a, input, select, .history-item, [role="button"]'
    const onOver = (e) => {
      const hit = Boolean(e.target.closest(INTERACTIVE))
      inner.classList.toggle('cursor-halo--active', hit)
      outer.classList.toggle('cursor-halo--active', hit)
    }
    document.addEventListener('mouseover', onOver)

    return () => {
      cancelAnimationFrame(rafId)
      document.removeEventListener('mousemove', onMove)
      document.removeEventListener('mouseover', onOver)
      inner.remove()
      outer.remove()
    }
  }, [])

  const {
    circuits,
    result,
    history,
    loading,
    error,
    loadParams,
    sweepData,
    sweepLoading,
    sweepProgress,
    runSimulation,
    loadSimulation,
    runSweep,
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
          sweepLoading={sweepLoading}
          loadParams={loadParams}
          onRun={runSimulation}
          onSweep={runSweep}
        />
        {/* key forces a remount on each new result, retriggering the CSS entry animation */}
        <ResultsPanel key={result?.simulation_id ?? 'empty'} result={result} />
      </main>

      {/* ── Noise Sweep Chart ───────────────────────────────────── */}
      {(sweepData || sweepLoading) && (
        <div className="sweep-section-wrapper">
          <FidelityChart
            sweepData={sweepData}
            sweepLoading={sweepLoading}
            sweepProgress={sweepProgress}
          />
        </div>
      )}

      {/* ── History ─────────────────────────────────────────────── */}
      <HistoryPanel history={history} onHistoryClick={loadSimulation} />

    </div>
  )
}
