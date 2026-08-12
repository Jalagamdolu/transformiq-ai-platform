"""AIOpportunity and Governance repositories."""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select

from app.db.models.ai_opportunity import AIOpportunity
from app.db.models.governance import Governance
from app.db.repositories.base import BaseRepository


class AIOpportunityRepository(BaseRepository[AIOpportunity]):
    model_class = AIOpportunity

    async def create_opportunity(
        self,
        organisation_id: uuid.UUID,
        name: str,
        category: str = "automation",
        status: str = "identified",
        process_id: Optional[uuid.UUID] = None,
        description: Optional[str] = None,
        ai_technology: Optional[str] = None,
    ) -> AIOpportunity:
        obj = AIOpportunity(
            organisation_id=organisation_id,
            process_id=process_id,
            name=name,
            description=description,
            category=category,
            status=status,
            ai_technology=ai_technology,
        )
        return await self.create(obj)


class GovernanceRepository(BaseRepository[Governance]):
    model_class = Governance

    async def get_by_opportunity(
        self,
        opportunity_id: uuid.UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> Tuple[List[Governance], int]:
        return await self.get_all(
            skip=skip, limit=limit, ai_opportunity_id=opportunity_id
        )

    async def create_governance(
        self,
        ai_opportunity_id: uuid.UUID,
        category: str,
        risk_level: str = "medium",
        description: Optional[str] = None,
        notes: Optional[str] = None,
    ) -> Governance:
        obj = Governance(
            ai_opportunity_id=ai_opportunity_id,
            category=category,
            description=description,
            risk_level=risk_level,
            notes=notes,
        )
        return await self.create(obj)
