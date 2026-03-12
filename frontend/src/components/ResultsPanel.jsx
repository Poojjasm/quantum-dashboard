/**
 * ResultsPanel.jsx — Simulation Results + Bar Chart
 * ===================================================
 * Shows after a simulation completes:
 *   - Circuit name, error rate, shots
 *   - Noise severity label
 *   - Bar chart: actual counts (blue) vs ideal counts (purple dashed)
 *   - Key stats: most common state, fidelity estimate
 */

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

// Register Chart.js components (required by react-chartjs-2 v5)
ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

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

  // Defensive guards: treat missing/null counts as empty objects, shots=0 as 1
  const safeCounts = counts || {}
  const safeIdeal  = ideal_counts || {}
  const safeShots  = shots > 0 ? shots : 1

  // Build chart data: all states that appear in either actual or ideal
  const allStates = Array.from(
    new Set([...Object.keys(safeCounts), ...Object.keys(safeIdeal)])
  ).sort()

  // If there are no states at all, show a fallback rather than crash
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
        backgroundColor: 'rgba(108, 99, 255, 0.8)',
        borderColor:     'rgba(108, 99, 255, 1)',
        borderWidth: 1,
        borderRadius: 4,
      },
      {
        label: 'Ideal (no noise)',
        data: idealValues,
        backgroundColor: 'rgba(0, 210, 255, 0.25)',
        borderColor:     'rgba(0, 210, 255, 0.9)',
        borderWidth: 2,
        borderRadius: 4,
        borderDash: [6, 3],
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#e2e8f0', font: { size: 13 } },
      },
      tooltip: {
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
        ticks: { color: '#94a3b8', font: { size: 13 } },
        grid:  { color: 'rgba(255,255,255,0.05)' },
      },
      y: {
        ticks: { color: '#94a3b8' },
        grid:  { color: 'rgba(255,255,255,0.05)' },
        title: {
          display: true,
          text: 'Count',
          color: '#94a3b8',
        },
      },
    },
  }

  // ── Stats ──────────────────────────────────────────────────────
  const topState = allStates.reduce((a, b) =>
    (safeCounts[a] || 0) >= (safeCounts[b] || 0) ? a : b
  )
  const topCount  = safeCounts[topState] || 0
  const topPct    = ((topCount / safeShots) * 100).toFixed(1)

  // Simple fidelity: fraction of shots that landed on an ideal state
  const idealStateSet = new Set(Object.keys(safeIdeal))
  const correctShots  = allStates
    .filter(s => idealStateSet.has(s))
    .reduce((sum, s) => sum + (safeCounts[s] || 0), 0)
  const fidelity = ((correctShots / safeShots) * 100).toFixed(1)

  // Noise level badge color
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
            {safeShots.toLocaleString()} shots · error rate {(error_rate * 100).toFixed(1)}%
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

      {/* ── Stats Row ──────────────────────────────────────────── */}
      <div className="stats-row">
        <div className="stat-card">
          <span className="stat-label">Top State</span>
          <span className="stat-value">{`|${topState}⟩`}</span>
          <span className="stat-sub">{topCount} shots ({topPct}%)</span>
        </div>
        <div className="stat-card">
          <span className="stat-label">Fidelity</span>
          <span className="stat-value">{fidelity}%</span>
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
