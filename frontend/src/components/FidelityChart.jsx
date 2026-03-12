/**
 * FidelityChart.jsx — Noise Sweep Fidelity Degradation Line Chart
 * ================================================================
 *
 * Shows how circuit fidelity degrades as error rate increases.
 * This is the key educational visualization of the whole project —
 * it answers: "at what noise level does this algorithm break down?"
 *
 * Chart contents:
 *   - Blue line:   measured fidelity at each error rate (with gradient fill)
 *   - Dashed line: 50% "coin flip" reference — at this point the circuit is
 *                  no better than a random guess
 *
 * Chart.js elements used here (not needed in the Bar chart):
 *   - LineElement   — draws the line between data points
 *   - PointElement  — draws the circle at each data point
 *   - Filler        — draws the gradient area under the line
 *
 * Props:
 *   sweepData     — { circuit, circuitName, points: [{errorRate, fidelity}] }
 *   sweepLoading  — bool; shows progress bar while sweep is running
 *   sweepProgress — int 0–8; how many points have been collected so far
 */

import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js'
import { Line } from 'react-chartjs-2'

// Register the Line-specific components.
// The Bar chart in ResultsPanel already registered CategoryScale,
// LinearScale, etc. — but LineElement, PointElement, and Filler
// are only needed here, so we register them here.
ChartJS.register(
  CategoryScale,
  LinearScale,
  LineElement,
  PointElement,
  Title,
  Tooltip,
  Legend,
  Filler,
)

// ── Gradient helper ────────────────────────────────────────────────
// Chart.js lets you pass a function as backgroundColor that receives
// the canvas context, letting you create a gradient tied to the chart.
// The gradient goes from a vivid color at the top (high fidelity) to
// transparent at the bottom (low fidelity), giving a glow effect.
function makeGradient(ctx, chartArea) {
  if (!chartArea) return 'rgba(108, 99, 255, 0.3)'
  const gradient = ctx.createLinearGradient(0, chartArea.top, 0, chartArea.bottom)
  gradient.addColorStop(0,   'rgba(108, 99, 255, 0.5)')
  gradient.addColorStop(0.5, 'rgba(0, 210, 255, 0.2)')
  gradient.addColorStop(1,   'rgba(0, 210, 255, 0.0)')
  return gradient
}

export default function FidelityChart({ sweepData, sweepLoading, sweepProgress }) {
  const TOTAL_POINTS = 8

  // ── Loading state — show progress bar ──────────────────────────
  if (sweepLoading) {
    const pct = Math.round((sweepProgress / TOTAL_POINTS) * 100)
    return (
      <section className="fidelity-section">
        <div className="fidelity-header">
          <h2 className="panel-title" style={{ margin: 0 }}>Noise Sweep</h2>
          <span className="sweep-progress-label">
            {sweepProgress}/{TOTAL_POINTS} simulations complete…
          </span>
        </div>
        <div className="sweep-progress-bar">
          <div
            className="sweep-progress-fill"
            style={{ width: `${pct}%` }}
            role="progressbar"
            aria-valuenow={pct}
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>
        <p className="sweep-progress-text">
          Running simulations at increasing error rates. Each point = 512 shots.
        </p>
      </section>
    )
  }

  if (!sweepData) return null

  const { circuitName, points } = sweepData

  // ── Build chart data ────────────────────────────────────────────
  const labels    = points.map(p => `${(p.errorRate * 100).toFixed(1)}%`)
  const fidelities = points.map(p => parseFloat(p.fidelity.toFixed(1)))

  // The 50% coin-flip reference line — same length as the data
  const coinFlip = points.map(() => 50)

  // Find where fidelity first drops below 50% — highlight this crossover
  const crossoverIdx = fidelities.findIndex(f => f < 50)
  const crossoverRate = crossoverIdx >= 0
    ? `${(points[crossoverIdx].errorRate * 100).toFixed(1)}%`
    : null

  const chartData = {
    labels,
    datasets: [
      {
        label: 'Fidelity',
        data: fidelities,
        borderColor: 'rgba(108, 99, 255, 1)',
        borderWidth: 2.5,
        pointBackgroundColor: fidelities.map(f =>
          f >= 75 ? 'rgba(74, 222, 128, 1)'   // green: working well
          : f >= 50 ? 'rgba(250, 204, 21, 1)' // yellow: degraded
          : 'rgba(248, 113, 113, 1)'           // red: broken
        ),
        pointRadius: 5,
        pointHoverRadius: 7,
        tension: 0.35,  // slight curve for smoother look
        fill: true,
        // Gradient fill: this function is called by Chart.js with the canvas context
        backgroundColor: (context) => {
          const { chart } = context
          return makeGradient(chart.ctx, chart.chartArea)
        },
      },
      {
        label: '50% (coin flip)',
        data: coinFlip,
        borderColor: 'rgba(248, 113, 113, 0.6)',
        borderWidth: 1.5,
        borderDash: [8, 4],
        pointRadius: 0,       // no dots on reference line
        fill: false,
        tension: 0,
      },
    ],
  }

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 800,
      easing: 'easeInOutQuart',
    },
    plugins: {
      legend: {
        labels: { color: '#e2e8f0', font: { size: 13 } },
      },
      tooltip: {
        callbacks: {
          title: (items) => `Error rate: ${items[0].label}`,
          label: (ctx) => {
            if (ctx.datasetIndex === 1) return ' Coin flip baseline: 50%'
            return ` Fidelity: ${ctx.raw}%`
          },
          afterBody: (items) => {
            const fidelity = items[0]?.raw
            if (fidelity === undefined) return []
            if (fidelity >= 90) return ['  Circuit working perfectly']
            if (fidelity >= 75) return ['  Circuit working well']
            if (fidelity >= 50) return ['  Circuit degraded but functional']
            return ['  Circuit has failed (worse than random)']
          },
        },
      },
    },
    scales: {
      x: {
        title: { display: true, text: 'Depolarizing Error Rate', color: '#94a3b8' },
        ticks: { color: '#94a3b8', font: { size: 12 } },
        grid: { color: 'rgba(255,255,255,0.05)' },
      },
      y: {
        title: { display: true, text: 'Fidelity (%)', color: '#94a3b8' },
        ticks: {
          color: '#94a3b8',
          callback: (v) => `${v}%`,
        },
        grid: { color: 'rgba(255,255,255,0.05)' },
        min: 0,
        max: 100,
      },
    },
  }

  return (
    <section className="fidelity-section">
      <div className="fidelity-header">
        <div>
          <h2 className="panel-title" style={{ margin: 0 }}>Noise Sweep — {circuitName}</h2>
          <p className="fidelity-subtitle">
            Fidelity at 8 error rates · 512 shots each
          </p>
        </div>
        {crossoverRate ? (
          <div className="crossover-badge">
            <span className="crossover-label">Breaks at</span>
            <span className="crossover-value">{crossoverRate}</span>
          </div>
        ) : (
          <div className="crossover-badge crossover-badge--resilient">
            <span className="crossover-label">Circuit resilient</span>
            <span className="crossover-value">above 50%</span>
          </div>
        )}
      </div>

      <div className="fidelity-chart-wrapper">
        <Line data={chartData} options={chartOptions} />
      </div>

      {/* Insight row */}
      <div className="sweep-insights">
        {points.map((p, i) => {
          const f = fidelities[i]
          const color = f >= 75 ? 'var(--color-success)'
            : f >= 50 ? 'var(--color-warning)'
            : 'var(--color-danger)'
          return (
            <div key={p.errorRate} className="sweep-point">
              <span className="sweep-point__rate">
                {(p.errorRate * 100).toFixed(1)}%
              </span>
              <span className="sweep-point__fidelity" style={{ color }}>
                {f.toFixed(0)}%
              </span>
            </div>
          )
        })}
      </div>
    </section>
  )
}
