"""Strategy model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.organisation import Organisation
    from app.db.models.value_chain import ValueChain


class Strategy(Base, UUIDMixin, TimestampMixin):
    """A high-level organisational strategy."""

    __tablename__ = "strategies"
    __table_args__ = (
        UniqueConstraint("organisation_id", "name", name="uq_strategy_org_name"),
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # active | draft | archived
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active", index=True
    )
    time_horizon: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship(
        "Organisation", back_populates="strategies"
    )
    value_chains: Mapped[List["ValueChain"]] = relationship(
        "ValueChain",
        back_populates="strategy",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Strategy id={self.id} name={self.name!r}>"
