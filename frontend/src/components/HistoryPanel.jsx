/**
 * HistoryPanel.jsx — Recent Simulations List
 * ============================================
 * Shows the last 10 simulations.
 * Clicking a row loads that simulation's result into the chart
 * and syncs the controls form — via onHistoryClick(sim) callback.
 */

const CIRCUIT_LABELS = {
  bell:          'Bell',
  ghz:           'GHZ',
  teleportation: 'Teleport',
  grover:        'Grover',
}

function noiseClass(errorRate) {
  if (errorRate === 0)    return 'noise-ideal'
  if (errorRate <= 0.01)  return 'noise-low'
  if (errorRate <= 0.05)  return 'noise-moderate'
  if (errorRate <= 0.10)  return 'noise-high'
  return 'noise-extreme'
}

export default function HistoryPanel({ history, onHistoryClick }) {
  if (!history || history.length === 0) {
    return (
      <section className="history-panel">
        <h3 className="panel-title">Recent Simulations</h3>
        <p className="history-empty">No simulations yet. Run one above!</p>
      </section>
    )
  }

  return (
    <section className="history-panel">
      <div className="history-header">
        <h3 className="panel-title" style={{ margin: 0 }}>Recent Simulations</h3>
        <span className="history-hint">Click any run to reload it</span>
      </div>

      <div className="history-list">
        {history.map(sim => (
          <button
            key={sim.id}
            className="history-item"
            onClick={() => onHistoryClick(sim)}
            title={`Load simulation #${sim.id} — ${CIRCUIT_LABELS[sim.circuit_id] || sim.circuit_id}, ${(sim.error_rate * 100).toFixed(1)}% error`}
            type="button"
          >
            <span className="history-id">#{sim.id}</span>
            <span className="history-circuit">
              {CIRCUIT_LABELS[sim.circuit_id] || sim.circuit_id}
            </span>
            <span className={`history-noise ${noiseClass(sim.error_rate)}`}>
              {(sim.error_rate * 100).toFixed(1)}% error
            </span>
            <span className="history-shots">
              {sim.shots.toLocaleString()} shots
            </span>
            <span className="history-time">
              {formatTime(sim.created_at)}
            </span>
          </button>
        ))}
      </div>
    </section>
  )
}

function formatTime(isoString) {
  if (!isoString) return ''
  try {
    const date = new Date(isoString.replace(' ', 'T'))
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return isoString
  }
}
