"""TransformationInitiative model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.associations import opportunity_initiatives
from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.ai_opportunity import AIOpportunity
    from app.db.models.organisation import Organisation


class TransformationInitiative(Base, UUIDMixin, TimestampMixin):
    """A discrete transformation initiative linking opportunities to delivery."""

    __tablename__ = "transformation_initiatives"

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # proposed | approved | planning | in_progress | completed | cancelled | on_hold
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="proposed", index=True
    )
    # Owner department or team
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="transformation_initiatives"
    )
    ai_opportunities: Mapped[List["AIOpportunity"]] = relationship(
        "AIOpportunity",
        secondary=opportunity_initiatives,
        back_populates="transformation_initiatives",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<TransformationInitiative id={self.id} name={self.name!r}>"
