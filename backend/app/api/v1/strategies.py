"""Strategy API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.strategy_repo import StrategyRepository
from app.schemas.common import PaginatedResponse
from app.schemas.strategy import (
    StrategyCreate,
    StrategyResponse,
)

router = APIRouter(prefix="/strategies", tags=["Strategies"])


@router.get("", response_model=PaginatedResponse[StrategyResponse])
async def list_strategies(
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[StrategyResponse]:
    repo = StrategyRepository(db)
    filters = {}
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[StrategyResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=StrategyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_strategy(
    payload: StrategyCreate,
    db: AsyncSession = Depends(get_db),
) -> StrategyResponse:
    repo = StrategyRepository(db)
    strategy = await repo.create_strategy(
        organisation_id=payload.organisation_id,
        name=payload.name,
        description=payload.description,
        status=payload.status,
        time_horizon=payload.time_horizon,
    )
    return StrategyResponse.from_orm_model(strategy)


@router.get("/{strategy_id}", response_model=StrategyResponse)
async def get_strategy(
    strategy_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> StrategyResponse:
    repo = StrategyRepository(db)
    strategy = await repo.get_by_id(strategy_id)
    if not strategy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Strategy {strategy_id} not found",
        )
    return StrategyResponse.from_orm_model(strategy)
