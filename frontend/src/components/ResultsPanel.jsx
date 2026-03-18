/**
 * ResultsPanel.jsx — Simulation Results + Bar Chart
 */

import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

// Count-up animation hook — animates a number from 0 to target over `duration`ms
function useCountUp(target, decimals = 1, duration = 750) {
  const [display, setDisplay] = useState('0.0')
  useEffect(() => {
    const targetNum = parseFloat(target)
    if (isNaN(targetNum)) return
    let startTime = null
    const animate = (timestamp) => {
      if (!startTime) startTime = timestamp
      const elapsed = timestamp - startTime
      const progress = Math.min(elapsed / duration, 1)
      // Ease out cubic
      const eased = 1 - Math.pow(1 - progress, 3)
      setDisplay((eased * targetNum).toFixed(decimals))
      if (progress < 1) requestAnimationFrame(animate)
    }
    requestAnimationFrame(animate)
  }, [target])
  return display
}

export default function ResultsPanel({ result }) {
  if (!result) {
    return (
      <section className="results-panel results-panel--empty">
        <div className="empty-state">
          <div className="empty-state__icon" aria-hidden="true">⚛</div>
          <h2 className="empty-state__title">No simulation yet</h2>
          <p className="empty-state__text">
            Choose a circuit and error rate, then click <strong>Run Simulation</strong>.
          </p>
        </div>
      </section>
    )
  }

  const { circuit_name, error_rate, shots, counts, ideal_counts, noise_label } = result

  // Defensive guards
  const safeCounts = counts || {}
  const safeIdeal  = ideal_counts || {}
  const safeShots  = shots > 0 ? shots : 1

  const allStates = Array.from(
    new Set([...Object.keys(safeCounts), ...Object.keys(safeIdeal)])
  ).sort()

  if (allStates.length === 0) {
    return (
      <section className="results-panel results-panel--empty">
        <div className="empty-state">
          <div className="empty-state__icon" aria-hidden="true">⚛</div>
          <h2 className="empty-state__title">No measurement data</h2>
          <p className="empty-state__text">The simulation returned no counts. Try running again.</p>
        </div>
      </section>
    )
  }

  const actualValues = allStates.map(s => safeCounts[s] || 0)
  const idealValues  = allStates.map(s => safeIdeal[s] || 0)

  const chartData = {
    labels: allStates.map(s => `|${s}⟩`),
    datasets: [
      {
        label: 'Simulated (with noise)',
        data: actualValues,
        backgroundColor: 'rgba(26, 79, 214, 0.7)',
        borderColor:     'rgba(26, 79, 214, 0.95)',
        borderWidth: 1,
        borderRadius: 3,
      },
      {
        label: 'Ideal (no noise)',
        data: idealValues,
        backgroundColor: 'rgba(224, 112, 0, 0.18)',
        borderColor:     'rgba(224, 112, 0, 0.85)',
        borderWidth: 2,
        borderRadius: 3,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: {
          color: '#7a7068',
          font: { size: 12, family: "'Inter', sans-serif" },
          boxWidth: 14,
        },
      },
      tooltip: {
        backgroundColor: 'rgba(255,255,255,0.97)',
        titleColor: '#1a1a18',
        bodyColor: '#7a7068',
        borderColor: '#ddd8ce',
        borderWidth: 1,
        callbacks: {
          label: ctx => {
            const pct = ((ctx.raw / safeShots) * 100).toFixed(1)
            return `${ctx.dataset.label}: ${ctx.raw} (${pct}%)`
          },
        },
      },
    },
    scales: {
      x: {
        ticks: {
          color: '#7a7068',
          font: { size: 13, family: "'Space Mono', monospace" },
        },
        grid: { color: 'rgba(0,0,0,0.05)' },
      },
      y: {
        ticks: { color: '#7a7068', font: { size: 12 } },
        grid:  { color: 'rgba(0,0,0,0.05)' },
        title: {
          display: true,
          text: 'Count',
          color: '#7a7068',
          font: { size: 12, family: "'Inter', sans-serif" },
        },
      },
    },
  }

  // Stats
  const topState  = allStates.reduce((a, b) =>
    (safeCounts[a] || 0) >= (safeCounts[b] || 0) ? a : b
  )
  const topCount  = safeCounts[topState] || 0
  const topPct    = ((topCount / safeShots) * 100).toFixed(1)

  const idealStateSet = new Set(Object.keys(safeIdeal))
  const correctShots  = allStates
    .filter(s => idealStateSet.has(s))
    .reduce((sum, s) => sum + (safeCounts[s] || 0), 0)
  const fidelity = ((correctShots / safeShots) * 100).toFixed(1)

  // Animated display values
  const fidelityDisplay = useCountUp(fidelity)
  const topPctDisplay   = useCountUp(topPct)

  // Handwritten annotation text based on noise level
  function getAnnotation(p) {
    if (p === 0)    return null
    if (p <= 0.01)  return 'very close to ideal — barely any difference'
    if (p <= 0.05)  return '← these extra states come from noise'
    if (p <= 0.10)  return 'noise is dominating — algorithm struggling'
    return 'nearly random — the circuit has broken down'
  }

  const annotation = getAnnotation(error_rate)

  function noiseBadgeClass(p) {
    if (p === 0)    return 'badge--ideal'
    if (p <= 0.01)  return 'badge--low'
    if (p <= 0.05)  return 'badge--moderate'
    if (p <= 0.10)  return 'badge--high'
    return 'badge--extreme'
  }

  return (
    <section className="results-panel">

      {/* ── Header ─────────────────────────────────────────────── */}
      <div className="results-header">
        <div>
          <h2 className="results-title">{circuit_name}</h2>
          <p className="results-subtitle">
            {safeShots.toLocaleString()} shots · {(error_rate * 100).toFixed(1)}% error rate
          </p>
        </div>
        <span className={`badge ${noiseBadgeClass(error_rate)}`}>
          {noise_label.split(' — ')[0]}
        </span>
      </div>

      <p className="results-noise-label">{noise_label}</p>

      {/* ── Chart ──────────────────────────────────────────────── */}
      <div className="chart-wrapper">
        <Bar data={chartData} options={chartOptions} />
      </div>

      {/* ── Handwritten annotation ──────────────────────────────── */}
      {annotation && (
        <div className="chart-callout">
          <span className="chart-callout__text">{annotation}</span>
        </div>
      )}

      {/* ── Stats Row ──────────────────────────────────────────── */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-label">Top State</span>
          <span className="stat-value">{`|${topState}⟩`}</span>
          <span className="stat-sub">{topCount} shots ({topPctDisplay}%)</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Fidelity</span>
          <span className="stat-value">{fidelityDisplay}%</span>
          <span className="stat-sub">shots on ideal states</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Total States</span>
          <span className="stat-value">{allStates.length}</span>
          <span className="stat-sub">distinct outcomes</span>
        </div>
      </div>

    </section>
  )
}
