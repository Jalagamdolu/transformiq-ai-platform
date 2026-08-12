/**
 * API client for the health endpoint.
 *
 * All fetch calls go through /api (proxied to http://localhost:8000 in dev
 * by Vite's server.proxy config).
 */

import type { HealthStatus } from '../types'

const API_BASE = '/api/v1'

export async function fetchHealth(): Promise<HealthStatus> {
  const response = await fetch(`${API_BASE}/health`, {
    method: 'GET',
    headers: { 'Content-Type': 'application/json' },
  })

  if (!response.ok) {
    throw new Error(`Health check failed with status ${response.status}`)
  }

  return response.json() as Promise<HealthStatus>
}
