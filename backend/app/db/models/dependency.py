"""Dependency model — flexible polymorphic dependency graph.

Allows any initiative or opportunity to depend on any other entity
(initiative, opportunity, process, or future capability).  Foreign key
constraints are intentionally omitted on the polymorphic ID columns so
the graph can span entity types without complex joined-table inheritance.

For Phase 2 this covers:
  initiative  →requires→  initiative
  initiative  →requires→  opportunity
  opportunity →requires→  process

Future phases can extend source/target entity types and add graph traversal
queries via recursive CTEs.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class Dependency(Base, UUIDMixin, TimestampMixin):
    """A directional dependency edge between two enterprise entities."""

    __tablename__ = "dependencies"

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # The entity that HAS the dependency
    # initiative | opportunity
    source_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    source_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    # What it depends on
    # initiative | opportunity | process | capability
    target_entity_type: Mapped[str] = mapped_column(String(50), nullable=False)
    target_entity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), nullable=False
    )

    # requires | enables | blocks
    relationship_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="requires"
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Dependency {self.source_entity_type}:{self.source_entity_id} "
            f"--{self.relationship_type}--> "
            f"{self.target_entity_type}:{self.target_entity_id}>"
        )
