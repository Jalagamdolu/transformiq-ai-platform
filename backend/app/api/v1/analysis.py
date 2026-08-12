"""Transformation Intelligence Analysis API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.models import AIOpportunity, Process
from app.schemas.analysis import (
    TransformationAnalysisInput,
    TransformationAnalysisResponse,
)
from app.schemas.common import PaginatedResponse
from app.services.analysis_service import AnalysisService

router = APIRouter(prefix="/analysis", tags=["Transformation Intelligence"])


@router.post(
    "/transformations",
    response_model=TransformationAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Run transformation intelligence analysis",
    description="Analyzes a scenario or entity using dynamic database relationships and deterministic scoring.",
)
async def analyze_transformation(
    payload: TransformationAnalysisInput,
    db: AsyncSession = Depends(get_db),
) -> TransformationAnalysisResponse:
    service = AnalysisService(db)
    try:
        analysis = await service.analyze_transformation(payload)
        return TransformationAnalysisResponse.from_orm_model(analysis)
    except ValueError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )


@router.post(
    "/opportunities/{opportunity_id}",
    response_model=TransformationAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze an existing AI Opportunity",
    description="Traverses PostgreSQL relationships starting from a known AI Opportunity.",
)
async def analyze_opportunity(
    opportunity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TransformationAnalysisResponse:
    # 1. Fetch opportunity
    stmt = select(AIOpportunity).where(AIOpportunity.id == opportunity_id)
    res = await db.execute(stmt)
    opp = res.scalar_one_or_none()
    if not opp:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"AI Opportunity {opportunity_id} not found",
        )

    # 2. Build analysis input
    payload = TransformationAnalysisInput(
        organisation_id=opp.organisation_id,
        title=f"Analysis of {opp.name}",
        description=opp.description,
        opportunity_id=opp.id,
        process_id=opp.process_id,
    )

    service = AnalysisService(db)
    analysis = await service.analyze_transformation(payload)
    return TransformationAnalysisResponse.from_orm_model(analysis)


@router.post(
    "/processes/{process_id}",
    response_model=TransformationAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze an existing Process",
    description="Traverses PostgreSQL relationships starting from a known Business Process.",
)
async def analyze_process(
    process_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TransformationAnalysisResponse:
    # 1. Fetch process
    stmt = select(Process).where(Process.id == process_id)
    res = await db.execute(stmt)
    proc = res.scalar_one_or_none()
    if not proc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {process_id} not found",
        )

    # 2. Build analysis input
    payload = TransformationAnalysisInput(
        organisation_id=proc.organisation_id,
        title=f"Process Transformation Analysis: {proc.name}",
        description=proc.description,
        process_id=proc.id,
    )

    service = AnalysisService(db)
    analysis = await service.analyze_transformation(payload)
    return TransformationAnalysisResponse.from_orm_model(analysis)


@router.get(
    "/transformations/{analysis_id}",
    response_model=TransformationAnalysisResponse,
    summary="Get persisted analysis result by ID",
)
async def get_analysis(
    analysis_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TransformationAnalysisResponse:
    service = AnalysisService(db)
    analysis = await service.get_analysis_by_id(analysis_id)
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {analysis_id} not found",
        )
    return TransformationAnalysisResponse.from_orm_model(analysis)


@router.get(
    "/transformations",
    response_model=PaginatedResponse[TransformationAnalysisResponse],
    summary="List persisted analyses for an organization",
)
async def list_analyses(
    organisation_id: uuid.UUID = Query(...),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TransformationAnalysisResponse]:
    from app.db.repositories.analysis_repo import AnalysisRepository

    repo = AnalysisRepository(db)
    items, total = await repo.get_by_organisation(
        organisation_id=organisation_id, skip=skip, limit=limit
    )
    return PaginatedResponse.create(
        items=[TransformationAnalysisResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )
