/**
 * useSimulation.js — Custom hook for all API communication
 * =========================================================
 *
 * This hook owns all data-fetching logic so components stay clean.
 * It exposes:
 *   - circuits       list of available circuits from /api/circuits
 *   - result         latest simulation result from /api/simulate
 *   - history        recent simulations from /api/history
 *   - loading        true while a simulation is running
 *   - error          error message string or null
 *   - runSimulation  function called by ControlsPanel on submit
 *   - clearError     function to dismiss the error banner
 *
 * API BASE URL:
 *   In dev:  Vite proxy forwards /api/* → http://localhost:5001/api/*
 *   In prod: import.meta.env.VITE_API_URL (set in Vercel dashboard)
 */

import { useState, useEffect, useCallback } from 'react'

// In production, VITE_API_URL is set as a Vercel environment variable.
// In dev, it's empty string — Vite's proxy handles /api/* → localhost:5001.
const API_BASE = import.meta.env.VITE_API_URL || ''

export function useSimulation() {
  const [circuits, setCircuits]   = useState([])
  const [result, setResult]       = useState(null)
  const [history, setHistory]     = useState([])
  const [loading, setLoading]     = useState(false)
  const [error, setError]         = useState(null)
  // loadParams: when set, ControlsPanel syncs its form to these values.
  // Set by loadSimulation() when user clicks a history item.
  const [loadParams, setLoadParams] = useState(null)

  // ── Fetch available circuits on mount ────────────────────────────
  useEffect(() => {
    fetch(`${API_BASE}/api/circuits`)
      .then(r => r.json())
      .then(data => setCircuits(data.circuits || []))
      .catch(() => setError('Could not load circuits. Is the backend running?'))
  }, [])

  // ── Fetch history (called after each simulation + on mount) ──────
  const fetchHistory = useCallback(() => {
    fetch(`${API_BASE}/api/history?limit=10`)
      .then(r => r.json())
      .then(data => setHistory(data.simulations || []))
      .catch(() => {}) // history is non-critical; silently fail
  }, [])

  useEffect(() => {
    fetchHistory()
  }, [fetchHistory])

  // ── Run a simulation ─────────────────────────────────────────────
  const runSimulation = useCallback(async ({ circuit, error_rate, shots }) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ circuit, error_rate, shots }),
      })

      const data = await response.json()

      if (!response.ok) {
        // Flask returned a structured error: { error: "...", code: "..." }
        throw new Error(data.error || `Server error ${response.status}`)
      }

      setResult(data)
      fetchHistory() // refresh history after each run
    } catch (err) {
      setError(err.message || 'Unknown error')
    } finally {
      setLoading(false)
    }
  }, [fetchHistory])

  // ── Load a past simulation by ID ─────────────────────────────
  // Called when user clicks a history item.
  // Fetches /api/results/<id>, rebuilds the result shape the
  // ResultsPanel expects, and syncs the ControlsPanel form.
  const loadSimulation = useCallback(async (sim) => {
    setLoading(true)
    setError(null)

    try {
      const response = await fetch(`${API_BASE}/api/results/${sim.id}`)
      const data = await response.json()

      if (!response.ok) {
        throw new Error(data.error || `Server error ${response.status}`)
      }

      // /api/results returns { simulation: {...}, results: [{state, count}, ...] }
      // Reshape into the same format runSimulation produces so ResultsPanel
      // doesn't need to know the difference.
      const countsObj = {}
      for (const row of data.results) {
        countsObj[row.state] = row.count
      }

      // Rebuild ideal_counts from the static distributions in the hook
      // by re-fetching nothing — we infer from circuit name.
      // Instead, just run a quick ideal fetch via simulate with error_rate=0
      // (this is fast — AerSimulator ideal path takes ~30ms).
      const idealResp = await fetch(`${API_BASE}/api/simulate`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          circuit: data.simulation.circuit_id,
          error_rate: 0,
          shots: data.simulation.shots,
        }),
      })
      const idealData = await idealResp.json()

      setResult({
        simulation_id: data.simulation.id,
        circuit:       data.simulation.circuit_id,
        circuit_name:  data.simulation.circuit_name,
        error_rate:    data.simulation.error_rate,
        shots:         data.simulation.shots,
        counts:        countsObj,
        ideal_counts:  idealData.counts,   // error_rate=0 gives us the ideal
        noise_label:   data.simulation.error_rate === 0
          ? 'Ideal (no noise) — theoretical perfect quantum computer'
          : `Loaded from history — error rate ${(data.simulation.error_rate * 100).toFixed(1)}%`,
      })

      // Sync the controls form to match this historical run
      setLoadParams({
        circuit:    data.simulation.circuit_id,
        error_rate: data.simulation.error_rate,
        shots:      data.simulation.shots,
      })

      fetchHistory()
    } catch (err) {
      setError(err.message || 'Failed to load simulation')
    } finally {
      setLoading(false)
    }
  }, [fetchHistory])

  // ── Noise Sweep ──────────────────────────────────────────────
  // Runs 8 simulations across the full error rate range for a given
  // circuit, one at a time so we can show live progress.
  // Result: sweepData = { circuit, circuitName, points: [{errorRate, fidelity},...] }
  const [sweepData, setSweepData]         = useState(null)
  const [sweepLoading, setSweepLoading]   = useState(false)
  const [sweepProgress, setSweepProgress] = useState(0)  // 0–8

  // The 8 error rates we sweep across.
  // Denser at the low end where the interesting physics happens.
  const SWEEP_RATES = [0, 0.005, 0.01, 0.02, 0.05, 0.10, 0.15, 0.20]

  const runSweep = useCallback(async (circuit, circuitName) => {
    setSweepLoading(true)
    setSweepProgress(0)
    setSweepData(null)
    setError(null)

    const points = []

    for (let i = 0; i < SWEEP_RATES.length; i++) {
      const rate = SWEEP_RATES[i]
      try {
        const resp = await fetch(`${API_BASE}/api/simulate`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          // 512 shots per sweep point — fast but statistically meaningful
          body: JSON.stringify({ circuit, error_rate: rate, shots: 512 }),
        })
        const data = await resp.json()
        if (!resp.ok) throw new Error(data.error || `Server error ${resp.status}`)

        // Fidelity = fraction of shots that landed on an ideal (expected) state.
        // At error_rate=0 this should be ~100%. At 0.20 it should be ~25-50%.
        const idealStates = new Set(Object.keys(data.ideal_counts))
        const correctShots = Object.entries(data.counts)
          .filter(([state]) => idealStates.has(state))
          .reduce((sum, [, count]) => sum + count, 0)
        const fidelity = (correctShots / data.shots) * 100

        points.push({ errorRate: rate, fidelity })
        // Update progress after each point so the UI can show a live counter
        setSweepProgress(i + 1)
      } catch (err) {
        setError(`Sweep failed at ${(rate * 100).toFixed(1)}% error rate: ${err.message}`)
        setSweepLoading(false)
        return
      }
    }

    setSweepData({ circuit, circuitName, points })
    fetchHistory()
    setSweepLoading(false)
  }, [fetchHistory])

  const clearError = useCallback(() => setError(null), [])

  return {
    circuits, result, history, loading, error, loadParams,
    sweepData, sweepLoading, sweepProgress,
    runSimulation, loadSimulation, runSweep, clearError,
  }
}
