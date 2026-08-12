/**
 * Intelligence API Client for TransformIQ Phase 5.
 */

const API_BASE = 'http://localhost:8000/api/v1'

export async function fetchOrganisations() {
  const resp = await fetch(`${API_BASE}/organisations`)
  if (!resp.ok) throw new Error('Failed to fetch organisations')
  return resp.json()
}

export async function fetchPriorities(orgId: string, category?: string) {
  let url = `${API_BASE}/intelligence/priorities?organisation_id=${orgId}`
  if (category) url += `&priority_category=${category}`
  const resp = await fetch(url)
  if (!resp.ok) throw new Error('Failed to fetch priorities')
  return resp.json()
}

export async function fetchSkills(orgId: string) {
  const resp = await fetch(`${API_BASE}/intelligence/skills?organisation_id=${orgId}`)
  if (!resp.ok) throw new Error('Failed to fetch skills')
  return resp.json()
}

export async function fetchGovernance(orgId: string) {
  const resp = await fetch(`${API_BASE}/intelligence/governance?organisation_id=${orgId}`)
  if (!resp.ok) throw new Error('Failed to fetch governance portfolio')
  return resp.json()
}

export async function fetchDependencyGraph(orgId: string) {
  const resp = await fetch(`${API_BASE}/intelligence/dependencies/graph?organisation_id=${orgId}`)
  if (!resp.ok) throw new Error('Failed to fetch dependency graph')
  return resp.json()
}

export async function queryAnalyst(orgId: string, query: string) {
  const resp = await fetch(`${API_BASE}/intelligence/analyst`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ organisation_id: orgId, query }),
  })
  if (!resp.ok) throw new Error('Failed to query executive analyst')
  return resp.json()
}

export async function runScenario(orgId: string, userInput: string) {
  const resp = await fetch(`${API_BASE}/analysis/scenarios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ organisation_id: orgId, user_input: userInput, force_refresh: true }),
  })
  if (!resp.ok) throw new Error('Failed to run scenario analysis')
  return resp.json()
}
