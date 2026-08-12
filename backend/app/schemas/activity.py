"""Activity schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

ActivityType = Literal["manual", "automated", "decision", "review"]
ActivityStatus = Literal["active", "inactive"]


class ActivityBase(BaseModel):
    process_id: uuid.UUID
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    status: ActivityStatus = "active"
    sequence_order: Optional[int] = Field(None, ge=0)


class ActivityCreate(ActivityBase):
    pass


class ActivityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    activity_type: Optional[ActivityType] = None
    status: Optional[ActivityStatus] = None
    sequence_order: Optional[int] = Field(None, ge=0)


class ActivityResponse(ActivityBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "ActivityResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
