"""API Router for Phase 5 Executive Transformation Intelligence Platform.

Exposes REST endpoints for C-suite decision support across the transformation chain:
- Transformation Priorities Ranking
- Process Intelligence Deep-Dive
- Role Intelligence (Automation vs Augmentation)
- Skill Intelligence (Workforce reskilling priorities)
- Governance Intelligence (Risk portfolio & audit controls)
- Dependency Intelligence (Interactive graph topology)
- Executive AI Analyst (Intent-routed assistant)

All endpoints enforce organisation_id multi-tenancy isolation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.analyst import AnalystQueryRequest, AnalystQueryResponse, ExecutiveAnalystService
from app.core.dependencies import get_db
from app.db.models import Organisation
from app.services.intelligence_service import (
    DependencyIntelligenceService,
    GovernanceIntelligenceService,
    PriorityIntelligenceService,
    ProcessIntelligenceService,
    RoleIntelligenceService,
    SkillIntelligenceService,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/intelligence", tags=["Executive Transformation Intelligence"])


async def _verify_organisation(organisation_id: UUID, db: AsyncSession) -> Organisation:
    """Helper to verify organisation exists for multi-tenant isolation."""
    stmt = select(Organisation).where(Organisation.id == organisation_id)
    res = await db.execute(stmt)
    org = res.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organisation with ID '{organisation_id}' not found.",
        )
    return org


@router.get(
    "/priorities",
    status_code=status.HTTP_200_OK,
    summary="Get ranked transformation priorities",
    description="Returns ranked transformation initiatives sorted by deterministic Phase 3 priority score.",
)
async def get_ranked_priorities(
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    priority_category: Optional[str] = Query(None, description="Filter by category: HIGH, MEDIUM, LOW"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Ranked priority intelligence endpoint."""
    await _verify_organisation(organisation_id, db)
    service = PriorityIntelligenceService(db)
    return await service.get_ranked_priorities(
        organisation_id=organisation_id,
        priority_category=priority_category,
        limit=limit,
        offset=offset,
    )


@router.get(
    "/processes/{process_id}",
    status_code=status.HTTP_200_OK,
    summary="Get process intelligence deep-dive",
    description="Returns deep-dive intelligence for a specific process including activities, AI opportunities, roles, skills, governance, and dependencies.",
)
async def get_process_intelligence(
    process_id: UUID,
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Process intelligence endpoint."""
    await _verify_organisation(organisation_id, db)
    service = ProcessIntelligenceService(db)
    result = await service.get_process_intelligence(organisation_id=organisation_id, process_id=process_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get(
    "/roles/{role_id}",
    status_code=status.HTTP_200_OK,
    summary="Get role transformation intelligence",
    description="Returns role intelligence breakdown classifying activities as potential automation vs potential augmentation.",
)
async def get_role_intelligence(
    role_id: UUID,
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Role intelligence endpoint."""
    await _verify_organisation(organisation_id, db)
    service = RoleIntelligenceService(db)
    result = await service.get_role_intelligence(organisation_id=organisation_id, role_id=role_id)
    if "error" in result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=result["error"])
    return result


@router.get(
    "/skills",
    status_code=status.HTTP_200_OK,
    summary="Get skill priorities and reskilling intelligence",
    description="Returns skill demand heatmap across high-priority opportunities and key reskilling focus areas.",
)
async def get_skill_intelligence(
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Skill intelligence endpoint."""
    await _verify_organisation(organisation_id, db)
    service = SkillIntelligenceService(db)
    return await service.get_skill_intelligence(organisation_id=organisation_id)


@router.get(
    "/governance",
    status_code=status.HTTP_200_OK,
    summary="Get governance risk portfolio",
    description="Returns governance risk portfolio, high-risk count, risk category breakdown, and human oversight mandates.",
)
async def get_governance_portfolio(
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    risk_level: Optional[str] = Query(None, description="Filter by risk level: high, medium, low"),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Governance intelligence endpoint."""
    await _verify_organisation(organisation_id, db)
    service = GovernanceIntelligenceService(db)
    return await service.get_governance_portfolio(organisation_id=organisation_id, risk_level=risk_level)


@router.get(
    "/dependencies/graph",
    status_code=status.HTTP_200_OK,
    summary="Get transformation graph topology",
    description="Returns interactive enterprise graph topology data (nodes, edges, cycle detection) for visual graph rendering.",
)
async def get_dependency_graph(
    organisation_id: UUID = Query(..., description="UUID of the organisation"),
    max_depth: int = Query(3, ge=1, le=5),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Dependency graph topology endpoint."""
    await _verify_organisation(organisation_id, db)
    service = DependencyIntelligenceService(db)
    return await service.get_dependency_graph(organisation_id=organisation_id, max_depth=max_depth)


@router.post(
    "/analyst",
    response_model=AnalystQueryResponse,
    status_code=status.HTTP_200_OK,
    summary="Ask the Executive AI Analyst",
    description="Routes C-suite natural language questions to deterministic backend intelligence services and synthesizes evidence-grounded briefings.",
)
async def query_executive_analyst(
    request: AnalystQueryRequest,
    db: AsyncSession = Depends(get_db),
) -> AnalystQueryResponse:
    """Executive AI Analyst query endpoint."""
    await _verify_organisation(request.organisation_id, db)
    analyst_service = ExecutiveAnalystService(db)
    return await analyst_service.process_executive_query(
        organisation_id=request.organisation_id, query=request.query
    )
