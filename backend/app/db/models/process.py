"""Process model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.activity import Activity
    from app.db.models.ai_opportunity import AIOpportunity
    from app.db.models.organisation import Organisation
    from app.db.models.value_chain import ValueChain


class Process(Base, UUIDMixin, TimestampMixin):
    """An enterprise business process within a value chain."""

    __tablename__ = "processes"
    __table_args__ = (
        UniqueConstraint("value_chain_id", "name", name="uq_process_vc_name"),
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    value_chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("value_chains.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # operational | support | management | strategic
    process_type: Mapped[str] = mapped_column(
        String(50), nullable=False, default="operational"
    )
    # active | inactive | under_review
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active", index=True
    )

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship("Organisation")
    value_chain: Mapped["ValueChain"] = relationship(
        "ValueChain", back_populates="processes"
    )
    activities: Mapped[List["Activity"]] = relationship(
        "Activity",
        back_populates="process",
        cascade="all, delete-orphan",
    )
    ai_opportunities: Mapped[List["AIOpportunity"]] = relationship(
        "AIOpportunity",
        back_populates="process",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Process id={self.id} name={self.name!r}>"
