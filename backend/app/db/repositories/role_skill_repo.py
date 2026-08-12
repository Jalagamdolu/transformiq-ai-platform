"""Role and Skill repositories."""

from __future__ import annotations

import uuid
from typing import Optional

from app.db.models.role import Role
from app.db.models.skill import Skill
from app.db.repositories.base import BaseRepository


class RoleRepository(BaseRepository[Role]):
    model_class = Role

    async def create_role(
        self,
        organisation_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        department: Optional[str] = None,
    ) -> Role:
        obj = Role(
            organisation_id=organisation_id,
            name=name,
            description=description,
            department=department,
        )
        return await self.create(obj)


class SkillRepository(BaseRepository[Skill]):
    model_class = Skill

    async def create_skill(
        self,
        organisation_id: uuid.UUID,
        name: str,
        skill_type: str = "technical",
        description: Optional[str] = None,
    ) -> Skill:
        obj = Skill(
            organisation_id=organisation_id,
            name=name,
            description=description,
            skill_type=skill_type,
        )
        return await self.create(obj)
