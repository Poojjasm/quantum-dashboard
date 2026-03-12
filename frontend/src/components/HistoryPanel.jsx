/**
 * HistoryPanel.jsx — Recent Simulations List
 * ============================================
 * Bottom bar showing the last 10 simulations from /api/history.
 * Clicking a row would load that simulation (future feature).
 */

// Circuit id → short display name
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

export default function HistoryPanel({ history }) {
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
      <h3 className="panel-title">Recent Simulations</h3>

      <div className="history-list">
        {history.map(sim => (
          <div key={sim.id} className="history-item">
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
          </div>
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
