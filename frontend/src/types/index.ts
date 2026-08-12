/** Shared TypeScript types mirroring backend Pydantic schemas. */

// ---------------------------------------------------------------------------
// Health
// ---------------------------------------------------------------------------

export interface HealthStatus {
  status: string
  version: string
  environment: string
  database: string
}

// ---------------------------------------------------------------------------
// UI state helpers
// ---------------------------------------------------------------------------

export type CheckState = 'checking' | 'ok' | 'error'
