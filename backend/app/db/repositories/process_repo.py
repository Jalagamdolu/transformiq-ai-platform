"""Process and Activity repositories."""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select

from app.db.models.activity import Activity
from app.db.models.process import Process
from app.db.repositories.base import BaseRepository


class ProcessRepository(BaseRepository[Process]):
    model_class = Process

    async def create_process(
        self,
        organisation_id: uuid.UUID,
        value_chain_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        process_type: str = "operational",
        status: str = "active",
    ) -> Process:
        obj = Process(
            organisation_id=organisation_id,
            value_chain_id=value_chain_id,
            name=name,
            description=description,
            process_type=process_type,
            status=status,
        )
        return await self.create(obj)


class ActivityRepository(BaseRepository[Activity]):
    model_class = Activity

    async def get_by_process(
        self, process_id: uuid.UUID, skip: int = 0, limit: int = 50
    ) -> Tuple[List[Activity], int]:
        return await self.get_all(skip=skip, limit=limit, process_id=process_id)

    async def create_activity(
        self,
        process_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        activity_type: Optional[str] = None,
        status: str = "active",
        sequence_order: Optional[int] = None,
    ) -> Activity:
        obj = Activity(
            process_id=process_id,
            name=name,
            description=description,
            activity_type=activity_type,
            status=status,
            sequence_order=sequence_order,
        )
        return await self.create(obj)
