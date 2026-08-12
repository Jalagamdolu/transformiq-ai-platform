"""Process API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.process_repo import ProcessRepository
from app.schemas.common import PaginatedResponse
from app.schemas.process import (
    ProcessCreate,
    ProcessResponse,
)

router = APIRouter(prefix="/processes", tags=["Processes"])


@router.get("", response_model=PaginatedResponse[ProcessResponse])
async def list_processes(
    value_chain_id: Optional[uuid.UUID] = Query(None),
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ProcessResponse]:
    repo = ProcessRepository(db)
    filters = {}
    if value_chain_id:
        filters["value_chain_id"] = value_chain_id
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[ProcessResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=ProcessResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_process(
    payload: ProcessCreate,
    db: AsyncSession = Depends(get_db),
) -> ProcessResponse:
    repo = ProcessRepository(db)
    process = await repo.create_process(
        organisation_id=payload.organisation_id,
        value_chain_id=payload.value_chain_id,
        name=payload.name,
        description=payload.description,
        process_type=payload.process_type,
        status=payload.status,
    )
    return ProcessResponse.from_orm_model(process)


@router.get("/{process_id}", response_model=ProcessResponse)
async def get_process(
    process_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProcessResponse:
    repo = ProcessRepository(db)
    process = await repo.get_by_id(process_id)
    if not process:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process {process_id} not found",
        )
    return ProcessResponse.from_orm_model(process)
