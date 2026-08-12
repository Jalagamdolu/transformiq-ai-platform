"""Strategy schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

StrategyStatus = Literal["active", "draft", "archived"]


class StrategyBase(BaseModel):
    organisation_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: StrategyStatus = "active"
    time_horizon: Optional[str] = Field(None, max_length=100)


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[StrategyStatus] = None
    time_horizon: Optional[str] = Field(None, max_length=100)


class StrategyResponse(StrategyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "StrategyResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
