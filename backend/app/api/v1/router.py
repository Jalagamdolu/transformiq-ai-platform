"""API v1 — aggregate router.

Aggregates all domain routers for Phase 2, Phase 3, Phase 4, and Phase 5.
"""

from fastapi import APIRouter

from app.api.v1 import (
    activities,
    analysis,
    health,
    initiatives,
    intelligence,
    opportunities,
    organisations,
    processes,
    roles,
    scenarios,
    skills,
    strategies,
    value_chains,
)

api_router = APIRouter()

# Phase 1
api_router.include_router(health.router, prefix="/health", tags=["Health"])

# Phase 2 Enterprise Domain
api_router.include_router(organisations.router)
api_router.include_router(strategies.router)
api_router.include_router(value_chains.router)
api_router.include_router(processes.router)
api_router.include_router(activities.router)
api_router.include_router(opportunities.router)
api_router.include_router(roles.router)
api_router.include_router(skills.router)
api_router.include_router(initiatives.router)

# Phase 3 Transformation Intelligence Engine
api_router.include_router(analysis.router)

# Phase 4A/4B AI & RAG Intelligence Scenarios
api_router.include_router(scenarios.router)

# Phase 5 Executive Transformation Intelligence Platform
api_router.include_router(intelligence.router)
