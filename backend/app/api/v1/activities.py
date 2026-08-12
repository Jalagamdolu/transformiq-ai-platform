"""Activity API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.process_repo import ActivityRepository
from app.schemas.activity import (
    ActivityCreate,
    ActivityResponse,
)
from app.schemas.common import PaginatedResponse

router = APIRouter(prefix="/activities", tags=["Activities"])


@router.get("", response_model=PaginatedResponse[ActivityResponse])
async def list_activities(
    process_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[ActivityResponse]:
    repo = ActivityRepository(db)
    filters = {}
    if process_id:
        filters["process_id"] = process_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[ActivityResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=ActivityResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_activity(
    payload: ActivityCreate,
    db: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    repo = ActivityRepository(db)
    act = await repo.create_activity(
        process_id=payload.process_id,
        name=payload.name,
        description=payload.description,
        activity_type=payload.activity_type,
        status=payload.status,
        sequence_order=payload.sequence_order,
    )
    return ActivityResponse.from_orm_model(act)


@router.get("/{activity_id}", response_model=ActivityResponse)
async def get_activity(
    activity_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ActivityResponse:
    repo = ActivityRepository(db)
    act = await repo.get_by_id(activity_id)
    if not act:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Activity {activity_id} not found",
        )
    return ActivityResponse.from_orm_model(act)
