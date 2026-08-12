"""Role model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.associations import activity_roles, opportunity_roles
from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.activity import Activity
    from app.db.models.ai_opportunity import AIOpportunity
    from app.db.models.organisation import Organisation


class Role(Base, UUIDMixin, TimestampMixin):
    """An organisational role (e.g. Demand Planner, Data Analyst)."""

    __tablename__ = "roles"
    __table_args__ = (
        UniqueConstraint("organisation_id", "name", name="uq_role_org_name"),
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(150), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="roles"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity", secondary=activity_roles, back_populates="roles"
    )
    ai_opportunities: Mapped[List["AIOpportunity"]] = relationship(
        "AIOpportunity", secondary=opportunity_roles, back_populates="roles"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Role id={self.id} name={self.name!r}>"
