"""AIOpportunity model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.associations import (
    opportunity_initiatives,
    opportunity_roles,
    opportunity_skills,
)
from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.governance import Governance
    from app.db.models.organisation import Organisation
    from app.db.models.process import Process
    from app.db.models.role import Role
    from app.db.models.skill import Skill
    from app.db.models.transformation_initiative import TransformationInitiative


class AIOpportunity(Base, UUIDMixin, TimestampMixin):
    """A potential AI use case identified for an enterprise process."""

    __tablename__ = "ai_opportunities"

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    process_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # automation | augmentation | analytics | generation | optimization
    category: Mapped[str] = mapped_column(
        String(50), nullable=False, default="automation"
    )
    # identified | assessed | approved | in_progress | implemented | rejected | on_hold
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="identified", index=True
    )
    # Optional short description of the AI technology (NLP, CV, ML etc.)
    ai_technology: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="ai_opportunities"
    )
    process: Mapped[Optional["Process"]] = relationship(
        "Process", back_populates="ai_opportunities"
    )
    governance_records: Mapped[List["Governance"]] = relationship(
        "Governance",
        back_populates="ai_opportunity",
        cascade="all, delete-orphan",
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=opportunity_roles, back_populates="ai_opportunities"
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill", secondary=opportunity_skills, back_populates="ai_opportunities"
    )
    transformation_initiatives: Mapped[List["TransformationInitiative"]] = relationship(
        "TransformationInitiative",
        secondary=opportunity_initiatives,
        back_populates="ai_opportunities",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<AIOpportunity id={self.id} name={self.name!r}>"
