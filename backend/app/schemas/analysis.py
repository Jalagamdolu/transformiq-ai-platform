"""Transformation Analysis Pydantic schemas."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

PriorityCategory = Literal["HIGH", "MEDIUM", "LOW"]


class FactorScoreDetail(BaseModel):
    score: float = Field(..., ge=0.0, le=100.0, description="Raw factor score (0-100)")
    weight: float = Field(..., ge=0.0, le=1.0, description="Factor weight in priority calculation")
    weighted_score: float = Field(..., ge=0.0, le=100.0, description="Contribution to total score")
    reason_codes: List[str] = Field(default_factory=list, description="Structured explanation reason codes")


class TransformationAnalysisInput(BaseModel):
    organisation_id: uuid.UUID
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    opportunity_id: Optional[uuid.UUID] = None
    process_id: Optional[uuid.UUID] = None
    strategy_id: Optional[uuid.UUID] = None


class TransformationAnalysisResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    organisation_id: uuid.UUID
    title: str
    description: Optional[str] = None
    status: str
    opportunity_id: Optional[uuid.UUID] = None
    process_id: Optional[uuid.UUID] = None
    strategy_id: Optional[uuid.UUID] = None

    priority_score: float
    priority_category: PriorityCategory

    factor_scores: Dict[str, FactorScoreDetail]
    reason_codes: Dict[str, List[str]]
    affected_entities: Dict[str, Any]
    governance_findings: List[Dict[str, Any]]
    dependency_findings: Dict[str, Any]

    engine_version: str
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "TransformationAnalysisResponse":
        raw_dict = {**obj.__dict__}  # type: ignore[attr-defined]
        return cls.model_validate(
            {
                **raw_dict,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
