"""Organisation repository."""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select

from app.db.models.organisation import Organisation
from app.db.repositories.base import BaseRepository


class OrganisationRepository(BaseRepository[Organisation]):
    model_class = Organisation

    async def get_by_name(self, name: str) -> Optional[Organisation]:
        stmt = select(Organisation).where(Organisation.name == name)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def create_organisation(
        self,
        name: str,
        industry: Optional[str] = None,
        description: Optional[str] = None,
        is_active: bool = True,
    ) -> Organisation:
        org = Organisation(
            name=name,
            industry=industry,
            description=description,
            is_active=is_active,
        )
        return await self.create(org)
