"""TransformationInitiative and Dependency API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.initiative_repo import (
    DependencyRepository,
    InitiativeRepository,
)
from app.schemas.common import PaginatedResponse
from app.schemas.dependency import (
    DependencyCreate,
    DependencyResponse,
)
from app.schemas.transformation_initiative import (
    TransformationInitiativeCreate,
    TransformationInitiativeResponse,
)

router = APIRouter(prefix="/initiatives", tags=["Transformation Initiatives"])


@router.get("", response_model=PaginatedResponse[TransformationInitiativeResponse])
async def list_initiatives(
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[TransformationInitiativeResponse]:
    repo = InitiativeRepository(db)
    filters = {}
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[TransformationInitiativeResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=TransformationInitiativeResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_initiative(
    payload: TransformationInitiativeCreate,
    db: AsyncSession = Depends(get_db),
) -> TransformationInitiativeResponse:
    repo = InitiativeRepository(db)
    init = await repo.create_initiative(
        organisation_id=payload.organisation_id,
        name=payload.name,
        status=payload.status,
        description=payload.description,
        department=payload.department,
    )
    return TransformationInitiativeResponse.from_orm_model(init)


@router.get("/{init_id}", response_model=TransformationInitiativeResponse)
async def get_initiative(
    init_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> TransformationInitiativeResponse:
    repo = InitiativeRepository(db)
    init = await repo.get_by_id(init_id)
    if not init:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transformation Initiative {init_id} not found",
        )
    return TransformationInitiativeResponse.from_orm_model(init)


# ── Sub-resource: Dependencies ────────────────────────────────────────────── #


@router.get("/{init_id}/dependencies", response_model=PaginatedResponse[DependencyResponse])
async def list_initiative_dependencies(
    init_id: uuid.UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[DependencyResponse]:
    init_repo = InitiativeRepository(db)
    init = await init_repo.get_by_id(init_id)
    if not init:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transformation Initiative {init_id} not found",
        )

    dep_repo = DependencyRepository(db)
    items, total = await dep_repo.get_for_entity(
        entity_type="initiative",
        entity_id=init_id,
        skip=skip,
        limit=limit,
    )
    return PaginatedResponse.create(
        items=[DependencyResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "/{init_id}/dependencies",
    response_model=DependencyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_initiative_dependency(
    init_id: uuid.UUID,
    payload: DependencyCreate,
    db: AsyncSession = Depends(get_db),
) -> DependencyResponse:
    init_repo = InitiativeRepository(db)
    init = await init_repo.get_by_id(init_id)
    if not init:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Transformation Initiative {init_id} not found",
        )

    dep_repo = DependencyRepository(db)
    dep = await dep_repo.create_dependency(
        organisation_id=payload.organisation_id,
        source_entity_type=payload.source_entity_type,
        source_entity_id=payload.source_entity_id,
        target_entity_type=payload.target_entity_type,
        target_entity_id=payload.target_entity_id,
        relationship_type=payload.relationship_type,
        description=payload.description,
    )
    return DependencyResponse.from_orm_model(dep)
