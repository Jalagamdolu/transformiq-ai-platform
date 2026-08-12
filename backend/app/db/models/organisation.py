"""Organisation model — root entity for multi-tenancy isolation."""

from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Boolean, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.ai_opportunity import AIOpportunity
    from app.db.models.role import Role
    from app.db.models.skill import Skill
    from app.db.models.strategy import Strategy
    from app.db.models.transformation_initiative import TransformationInitiative


class Organisation(Base, UUIDMixin, TimestampMixin):
    """An enterprise organisation (tenant root)."""

    __tablename__ = "organisations"

    name: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    industry: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    strategies: Mapped[List["Strategy"]] = relationship(
        "Strategy",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    roles: Mapped[List["Role"]] = relationship(
        "Role",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    ai_opportunities: Mapped[List["AIOpportunity"]] = relationship(
        "AIOpportunity",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )
    transformation_initiatives: Mapped[List["TransformationInitiative"]] = relationship(
        "TransformationInitiative",
        back_populates="organisation",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Organisation id={self.id} name={self.name!r}>"
