"""Governance schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

GovernanceCategory = Literal[
    "privacy",
    "security",
    "bias_fairness",
    "explainability",
    "human_oversight",
    "model_risk",
    "compliance",
    "monitoring",
]
RiskLevel = Literal["low", "medium", "high", "critical"]


class GovernanceBase(BaseModel):
    ai_opportunity_id: uuid.UUID
    category: GovernanceCategory
    description: Optional[str] = None
    risk_level: RiskLevel = "medium"
    notes: Optional[str] = None


class GovernanceCreate(GovernanceBase):
    pass


class GovernanceUpdate(BaseModel):
    description: Optional[str] = None
    risk_level: Optional[RiskLevel] = None
    notes: Optional[str] = None


class GovernanceResponse(GovernanceBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "GovernanceResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
