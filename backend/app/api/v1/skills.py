"""Skill API endpoints."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.db.repositories.role_skill_repo import SkillRepository
from app.schemas.common import PaginatedResponse
from app.schemas.skill import (
    SkillCreate,
    SkillResponse,
)

router = APIRouter(prefix="/skills", tags=["Skills"])


@router.get("", response_model=PaginatedResponse[SkillResponse])
async def list_skills(
    organisation_id: Optional[uuid.UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
) -> PaginatedResponse[SkillResponse]:
    repo = SkillRepository(db)
    filters = {}
    if organisation_id:
        filters["organisation_id"] = organisation_id
    items, total = await repo.get_all(skip=skip, limit=limit, **filters)
    return PaginatedResponse.create(
        items=[SkillResponse.from_orm_model(i) for i in items],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.post(
    "",
    response_model=SkillResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_skill(
    payload: SkillCreate,
    db: AsyncSession = Depends(get_db),
) -> SkillResponse:
    repo = SkillRepository(db)
    skill = await repo.create_skill(
        organisation_id=payload.organisation_id,
        name=payload.name,
        skill_type=payload.skill_type,
        description=payload.description,
    )
    return SkillResponse.from_orm_model(skill)


@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill(
    skill_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> SkillResponse:
    repo = SkillRepository(db)
    skill = await repo.get_by_id(skill_id)
    if not skill:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Skill {skill_id} not found",
        )
    return SkillResponse.from_orm_model(skill)
