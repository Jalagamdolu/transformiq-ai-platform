"""TransformationInitiative schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

InitiativeStatus = Literal[
    "proposed", "approved", "planning", "in_progress",
    "completed", "cancelled", "on_hold",
]


class TransformationInitiativeBase(BaseModel):
    organisation_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    status: InitiativeStatus = "proposed"
    department: Optional[str] = Field(None, max_length=150)


class TransformationInitiativeCreate(TransformationInitiativeBase):
    pass


class TransformationInitiativeUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    status: Optional[InitiativeStatus] = None
    department: Optional[str] = Field(None, max_length=150)


class TransformationInitiativeResponse(TransformationInitiativeBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "TransformationInitiativeResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
