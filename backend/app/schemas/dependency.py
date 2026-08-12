"""Dependency schemas."""

from __future__ import annotations

import uuid
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

EntityType = Literal["initiative", "opportunity", "process", "capability"]
RelationshipType = Literal["requires", "enables", "blocks"]


class DependencyBase(BaseModel):
    organisation_id: uuid.UUID
    source_entity_type: EntityType
    source_entity_id: uuid.UUID
    target_entity_type: EntityType
    target_entity_id: uuid.UUID
    relationship_type: RelationshipType = "requires"
    description: Optional[str] = None


class DependencyCreate(DependencyBase):
    pass


class DependencyResponse(DependencyBase):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    created_at: str
    updated_at: str

    @classmethod
    def from_orm_model(cls, obj: object) -> "DependencyResponse":
        return cls.model_validate(
            {
                **obj.__dict__,
                "created_at": obj.created_at.isoformat(),  # type: ignore[attr-defined]
                "updated_at": obj.updated_at.isoformat(),  # type: ignore[attr-defined]
            }
        )
