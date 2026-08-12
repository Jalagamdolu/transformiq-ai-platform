"""Strategy and ValueChain repositories."""

from __future__ import annotations

import uuid
from typing import List, Optional, Tuple

from sqlalchemy import select

from app.db.models.strategy import Strategy
from app.db.models.value_chain import ValueChain
from app.db.repositories.base import BaseRepository


class StrategyRepository(BaseRepository[Strategy]):
    model_class = Strategy

    async def create_strategy(
        self,
        organisation_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
        status: str = "active",
        time_horizon: Optional[str] = None,
    ) -> Strategy:
        obj = Strategy(
            organisation_id=organisation_id,
            name=name,
            description=description,
            status=status,
            time_horizon=time_horizon,
        )
        return await self.create(obj)


class ValueChainRepository(BaseRepository[ValueChain]):
    model_class = ValueChain

    async def create_value_chain(
        self,
        organisation_id: uuid.UUID,
        strategy_id: uuid.UUID,
        name: str,
        description: Optional[str] = None,
    ) -> ValueChain:
        obj = ValueChain(
            organisation_id=organisation_id,
            strategy_id=strategy_id,
            name=name,
            description=description,
        )
        return await self.create(obj)
