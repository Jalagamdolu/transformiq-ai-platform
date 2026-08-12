"""Role API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.role_skill_repo import RoleRepository
from app.schemas.common import PaginatedResponse
from app.schemas.role import (
    RoleCreate,
    RoleResponse,
)

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=PaginatedResponse[RoleResponse])
async def list_roles(
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[RoleResponse]:
    repo = RoleRepository(db)
    filters = {}
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[RoleResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=RoleResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_role(
    payload: RoleCreate,
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    repo = RoleRepository(db)
    role = await repo.create_role(
        organisation_id=payload.organisation_id,
        name=payload.name,
        description=payload.description,
        department=payload.department,
    )
    return RoleResponse.from_orm_model(role)


@router.get("/{role_id}", response_model=RoleResponse)
async def get_role(
    role_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> RoleResponse:
    repo = RoleRepository(db)
    role = await repo.get_by_id(role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role {role_id} not found",
        )
    return RoleResponse.from_orm_model(role)
