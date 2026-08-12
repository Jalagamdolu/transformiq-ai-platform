# TransformIQ — Architecture

## Overview

TransformIQ is a three-tier web application with strict layer boundaries.

```
┌─────────────────────────────────┐
│   Frontend (React + TS + Vite)  │  Port 5173
└────────────────┬────────────────┘
                 │ REST /api/v1/*
┌────────────────▼────────────────┐
│    Backend (Python + FastAPI)   │  Port 8000
│  ┌──────────────────────────┐   │
│  │  api/v1/     (HTTP only) │   │
│  │  schemas/    (contracts) │   │
│  │  engines/    (logic)     │   │
│  │  ai/         (LLM)       │   │
│  │  rag/        (retrieval) │   │
│  └──────────┬───────────────┘   │
└─────────────┼───────────────────┘
              │ asyncpg
┌─────────────▼───────────────────┐
│  PostgreSQL 15 + pgvector       │  Port 5432
└─────────────────────────────────┘
```

## Layer Boundaries

| Layer | Allowed to call | Forbidden |
|---|---|---|
| `api/v1/` | `schemas/`, `engines/`, `db/repositories/` | No business logic |
| `schemas/` | Nothing | No DB, no engines |
| `engines/` | `ai/`, `rag/`, `schemas/` | No HTTP, no direct DB |
| `ai/` | External LLM APIs | No DB, no business logic |
| `rag/` | `ai/`, `db/repositories/` | No business logic |
| `db/repositories/` | SQLAlchemy session | No business logic |

## Domain Model (Planned — Phase 2+)

```
Organisation (tenant root)
└── Strategy
    └── ValueChain (1..n)
        └── Process (1..n)
            └── Activity (1..n)
                ├── AIOpportunity (1..n)  ← scored by scoring engine
                ├── Role (m..n)
                └── Skill (m..n)

GovernancePolicy (1..n) → links to Process / Activity
TransformationInitiative (1..n) → output of analysis, links to AIOpportunity
```

## Database Strategy

- **ORM**: SQLAlchemy 2.0 async with `asyncpg`
- **pgvector**: Used for semantic retrieval in the RAG layer; not added to every entity by default
- **Migrations**: Alembic with auto-generate. All schema changes are versioned.
- **Repository pattern**: All SQL in `db/repositories/`. No raw queries in routes or engines.
- **Tenant isolation**: `organisation_id` foreign key on every top-level entity (ready for Phase 2+ multi-tenancy)

## LLM Abstraction (Phase 2+)

The `ai/client.py` module wraps the LLM provider behind a common interface. Switching from Ollama to OpenAI or Anthropic requires only a config change (`LLM_PROVIDER`).

```
LLM_PROVIDER=ollama   → OllamaClient
LLM_PROVIDER=openai   → OpenAIClient  (Phase 2+)
LLM_PROVIDER=anthropic → AnthropicClient  (Phase 2+)
```

## Scaling Considerations

- Engines are pure functions — stateless and safe to parallelise
- pgvector HNSW/IVFFlat indexes support semantic search at 1,000+ process scale
- FastAPI `BackgroundTasks` used for long-running analysis; can later migrate to Celery with zero API changes
- Repository pattern means DB queries can be optimised without touching business logic

## Decisions

| Decision | Choice | Rationale |
|---|---|---|
| Auth | None (Phase 1) | Two-day challenge; data model is tenant-ready |
| State management (FE) | Zustand | Lighter than Redux for this scope |
| CSS | Vanilla CSS | Full control, no build complexity |
| Document upload | Not in MVP | Scope control; data is seeded |
| SSR | No (Vite SPA) | Not needed for enterprise internal tool |
| Microservices | No | Single FastAPI service is sufficient for 1,000+ processes |
