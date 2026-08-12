"""AIOpportunity and Governance API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.opportunity_repo import (
    AIOpportunityRepository,
    GovernanceRepository,
)
from app.schemas.ai_opportunity import (
    AIOpportunityCreate,
    AIOpportunityResponse,
)
from app.schemas.common import PaginatedResponse
from app.schemas.governance import (
    GovernanceCreate,
    GovernanceResponse,
)

router = APIRouter(prefix="/opportunities", tags=["AI Opportunities"])


@router.get("", response_model=PaginatedResponse[AIOpportunityResponse])
async def list_opportunities(
    process_id: Optional[uuid.UUID] = Query(None),
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[AIOpportunityResponse]:
    repo = AIOpportunityRepository(db)
    filters = {}
    if process_id:
        filters["process_id"] = process_id
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[AIOpportunityResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=AIOpportunityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_opportunity(
    payload: AIOpportunityCreate,
    db: AsyncSession = Depends(get_db),
) -> AIOpportunityResponse:
    repo = AIOpportunityRepository(db)
    opp = await repo.create_opportunity(
        organisation_id=payload.organisation_id,
        name=payload.name,
        category=payload.category,
        status=payload.status,
        process_id=payload.process_id,
        description=payload.description,
        ai_technology=payload.ai_technology,
    )
    return AIOpportunityResponse.from_orm_model(opp)


@router.get("/{opp_id}", response_model=AIOpportunityResponse)
async def get_opportunity(
    opp_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> AIOpportunityResponse:
    repo = AIOpportunityRepository(db)
    opp = await repo.get_by_id(opp_id)
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Opportunity {opp_id} not found",
        )
    return AIOpportunityResponse.from_orm_model(opp)


# ── Sub-resource: Governance ──────────────────────────────────────────────── #


@router.get("/{opp_id}/governance", response_model=PaginatedResponse[GovernanceResponse])
async def list_opportunity_governance(
    opp_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[GovernanceResponse]:
    # Ensure opportunity exists
    opp_repo = AIOpportunityRepository(db)
    opp = await opp_repo.get_by_id(opp_id)
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Opportunity {opp_id} not found",
        )

    gov_repo = GovernanceRepository(db)
    items, total = await gov_repo.get_by_opportunity(opp_id, skip=skip, limit=limit)
    return PaginatedResponse.create(
        items=[GovernanceResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{opp_id}/governance",
    response_model=GovernanceResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_opportunity_governance(
    opp_id: uuid.UUID,
    payload: GovernanceCreate,
    db: AsyncSession = Depends(get_db),
) -> GovernanceResponse:
    opp_repo = AIOpportunityRepository(db)
    opp = await opp_repo.get_by_id(opp_id)
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Opportunity {opp_id} not found",
        )

    gov_repo = GovernanceRepository(db)
    gov = await gov_repo.create_governance(
        ai_opportunity_id=opp_id,
        category=payload.category,
        risk_level=payload.risk_level,
        description=payload.description,
        notes=payload.notes,
    )
    return GovernanceResponse.from_orm_model(gov)
