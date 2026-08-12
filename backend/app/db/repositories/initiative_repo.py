"""TransformationInitiative and Dependency repositories."""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import or_, select

from app.db.models.dependency import Dependency
from app.db.models.transformation_initiative import TransformationInitiative
from app.db.repositories.base import BaseRepository


class InitiativeRepository(BaseRepository[TransformationInitiative]):
    model_class = TransformationInitiative

    async def create_initiative(
        self,
        organisation_id: uuid.UUID,
        name: str,
        status: str = "proposed",
        description: Optional[str] = None,
        department: Optional[str] = None,
    ) -> TransformationInitiative:
        obj = TransformationInitiative(
            organisation_id=organisation_id,
            name=name,
            description=description,
            status=status,
            department=department,
        )
        return await self.create(obj)


class DependencyRepository(BaseRepository[Dependency]):
    model_class = Dependency

    async def get_for_entity(
        self,
        entity_type: str,
        entity_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Dependency], int]:
        """Return all dependencies where the entity is source OR target."""
        from sqlalchemy import func

        count_stmt = (
            select(func.count())
            .select_from(Dependency)
            .where(
                or_(
                    (Dependency.source_entity_type == entity_type)
                    & (Dependency.source_entity_id == entity_id),
                    (Dependency.target_entity_type == entity_type)
                    & (Dependency.target_entity_id == entity_id),
                )
            )
        )
        list_stmt = (
            select(Dependency)
            .where(
                or_(
                    (Dependency.source_entity_type == entity_type)
                    & (Dependency.source_entity_id == entity_id),
                    (Dependency.target_entity_type == entity_type)
                    & (Dependency.target_entity_id == entity_id),
                )
            )
            .offset(skip)
            .limit(limit)
        )
        total = (await self.session.execute(count_stmt)).scalar_one()
        rows = (await self.session.execute(list_stmt)).scalars().all()
        return list(rows), total

    async def create_dependency(
        self,
        organisation_id: uuid.UUID,
        source_entity_type: str,
        source_entity_id: uuid.UUID,
        target_entity_type: str,
        target_entity_id: uuid.UUID,
        relationship_type: str = "requires",
        description: Optional[str] = None,
    ) -> Dependency:
        obj = Dependency(
            organisation_id=organisation_id,
            source_entity_type=source_entity_type,
            source_entity_id=source_entity_id,
            target_entity_type=target_entity_type,
            target_entity_id=target_entity_id,
            relationship_type=relationship_type,
            description=description,
        )
        return await self.create(obj)
