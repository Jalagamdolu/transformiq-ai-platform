"""ValueChain API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.strategy_repo import ValueChainRepository
from app.schemas.common import PaginatedResponse
from app.schemas.value_chain import (
    ValueChainCreate,
    ValueChainResponse,
)

router = APIRouter(prefix="/value-chains", tags=["Value Chains"])


@router.get("", response_model=PaginatedResponse[ValueChainResponse])
async def list_value_chains(
    strategy_id: Optional[uuid.UUID] = Query(None),
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ValueChainResponse]:
    repo = ValueChainRepository(db)
    filters = {}
    if strategy_id:
        filters["strategy_id"] = strategy_id
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[ValueChainResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=ValueChainResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_value_chain(
    payload: ValueChainCreate,
    db: AsyncSession = Depends(get_db),
) -> ValueChainResponse:
    repo = ValueChainRepository(db)
    vc = await repo.create_value_chain(
        organisation_id=payload.organisation_id,
        strategy_id=payload.strategy_id,
        name=payload.name,
        description=payload.description,
    )
    return ValueChainResponse.from_orm_model(vc)


@router.get("/{vc_id}", response_model=ValueChainResponse)
async def get_value_chain(
    vc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ValueChainResponse:
    repo = ValueChainRepository(db)
    vc = await repo.get_by_id(vc_id)
    if not vc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Value Chain {vc_id} not found",
        )
    return ValueChainResponse.from_orm_model(vc)
