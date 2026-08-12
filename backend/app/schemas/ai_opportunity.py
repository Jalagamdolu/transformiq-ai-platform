"""AI Opportunity schemas."""

from __future__ import annotations

import uuid
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

OpportunityCategory = Literal[
    "automation", "augmentation", "analytics", "generation", "optimization"
]
OpportunityStatus = Literal[
    "identified", "assessed", "approved", "in_progress",
    "implemented", "rejected", "on_hold",
]


class AIOpportunityBase(BaseModel):
    organisation_id: uuid.UUID
    process_id: Optional[uuid.UUID] = None
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    category: OpportunityCategory = "automation"
    status: OpportunityStatus = "identified"
    ai_technology: Optional[str] = Field(None, max_length=100)


class AIOpportunityCreate(AIOpportunityBase):
    pass


class AIOpportunityUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[OpportunityCategory] = None
    status: Optional[OpportunityStatus] = None
    ai_technology: Optional[str] = Field(None, max_length=100)
    process_id: Optional[uuid.UUID] = None


class AIOpportunityResponse(AIOpportunityBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "AIOpportunityResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
