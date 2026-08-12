"""Generic base repository with typed CRUD operations.

Each entity repository subclasses BaseRepository and sets `model_class`.
Entity-specific queries (e.g. filter by organisation_id) are added in the
subclass.
"""

from __future__ import annotations

import uuid
from typing import Any, Generic, List, Optional, Tuple, Type, TypeVar

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Generic async CRUD repository."""

    model_class: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # ── Read ──────────────────────────────────────────────────────────────── #

    async def get_by_id(self, id: uuid.UUID) -> Optional[ModelT]:
        """Return a single instance by primary key, or None."""
        return await self.session.get(self.model_class, id)

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 20,
        **filters: Any,
    ) -> Tuple[List[ModelT], int]:
        """Return a paginated list and total count.

        Keyword arguments are applied as equality filters on the model columns,
        e.g. ``organisation_id=uuid.UUID(...)``.
        """
        count_stmt = select(func.count()).select_from(self.model_class)
        list_stmt = select(self.model_class)

        for column_name, value in filters.items():
            if value is not None:
                col = getattr(self.model_class, column_name)
                count_stmt = count_stmt.where(col == value)
                list_stmt = list_stmt.where(col == value)

        total: int = (await self.session.execute(count_stmt)).scalar_one()
        rows = (
            await self.session.execute(list_stmt.offset(skip).limit(limit))
        ).scalars().all()

        return list(rows), total

    # ── Write ─────────────────────────────────────────────────────────────── #

    async def create(self, instance: ModelT) -> ModelT:
        """Persist a new instance and return it with server-populated fields."""
        self.session.add(instance)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def update(self, instance: ModelT, **updates: Any) -> ModelT:
        """Apply field updates to an existing instance."""
        for field, value in updates.items():
            if value is not None:
                setattr(instance, field, value)
        await self.session.flush()
        await self.session.refresh(instance)
        return instance

    async def delete(self, id: uuid.UUID) -> bool:
        """Delete by primary key. Returns True if the row existed."""
        instance = await self.get_by_id(id)
        if instance is None:
            return False
        await self.session.delete(instance)
        await self.session.flush()
        return True
