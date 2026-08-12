"""Value chain schemas."""

from __future__ import annotations

import uuid
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class ValueChainBase(BaseModel):
    organisation_id: uuid.UUID
    strategy_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None


class ValueChainCreate(ValueChainBase):
    pass


class ValueChainUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None


class ValueChainResponse(ValueChainBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "ValueChainResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
