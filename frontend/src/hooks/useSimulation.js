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

  const clearError = useCallback(() => setError(null), [])

  return { circuits, result, history, loading, error, runSimulation, clearError }
}
