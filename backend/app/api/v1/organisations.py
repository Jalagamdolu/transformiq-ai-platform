"""Organisation API endpoints."""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.organisation_repo import OrganisationRepository
from app.schemas.common import PaginatedResponse
from app.schemas.organisation import (
    OrganisationCreate,
    OrganisationResponse,
)

router = APIRouter(prefix="/organisations", tags=["Organisations"])


@router.get("", response_model=PaginatedResponse[OrganisationResponse])
async def list_organisations(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[OrganisationResponse]:
    repo = OrganisationRepository(db)
    items, total = await repo.get_all(skip=skip, limit=limit)
    return PaginatedResponse.create(
        items=[OrganisationResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=OrganisationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_organisation(
    payload: OrganisationCreate,
    db: AsyncSession = Depends(get_db),
) -> OrganisationResponse:
    repo = OrganisationRepository(db)
    existing = await repo.get_by_name(payload.name)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Organisation with name '{payload.name}' already exists",
        )
    org = await repo.create_organisation(
        name=payload.name,
        industry=payload.industry,
        description=payload.description,
        is_active=payload.is_active,
    )
    return OrganisationResponse.from_orm_model(org)


@router.get("/{org_id}", response_model=OrganisationResponse)
async def get_organisation(
    org_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> OrganisationResponse:
    repo = OrganisationRepository(db)
    org = await repo.get_by_id(org_id)
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organisation {org_id} not found",
        )
    return OrganisationResponse.from_orm_model(org)
