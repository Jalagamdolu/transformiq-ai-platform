"""Process schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ProcessType = Literal["operational", "support", "management", "strategic"]
ProcessStatus = Literal["active", "inactive", "under_review"]


class ProcessBase(BaseModel):
    organisation_id: uuid.UUID
    value_chain_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    process_type: ProcessType = "operational"
    status: ProcessStatus = "active"


class ProcessCreate(ProcessBase):
    pass


class ProcessUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    process_type: Optional[ProcessType] = None
    status: Optional[ProcessStatus] = None


class ProcessResponse(ProcessBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "ProcessResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
