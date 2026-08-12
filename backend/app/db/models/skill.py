"""Skill model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.associations import activity_skills, opportunity_skills
from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.activity import Activity
    from app.db.models.ai_opportunity import AIOpportunity
    from app.db.models.organisation import Organisation


class Skill(Base, UUIDMixin, TimestampMixin):
    """A current or future organisational capability/skill."""

    __tablename__ = "skills"
    __table_args__ = (
        UniqueConstraint("organisation_id", "name", name="uq_skill_org_name"),
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # technical | business | ai_literacy | data | leadership
    skill_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="technical"
    )

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="skills"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", secondary=activity_skills, back_populates="skills"
    )
    ai_opportunities: Mapped[List["AIOpportunity"]] = relationship(
        "AIOpportunity", secondary=opportunity_skills, back_populates="skills"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Skill id={self.id} name={self.name!r}>"
