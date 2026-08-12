"""ValueChain model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.organisation import Organisation
    from app.db.models.process import Process
    from app.db.models.strategy import Strategy


class ValueChain(Base, UUIDMixin, TimestampMixin):
    """A value-chain area within a strategy (e.g. Supply Chain, Store Operations)."""

    __tablename__ = "value_chains"
    __table_args__ = (
        UniqueConstraint("strategy_id", "name", name="uq_valuechain_strategy_name"),
    )

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    strategy_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped["Organisation"] = relationship("Organisation")
    strategy: Mapped["Strategy"] = relationship(
        "Strategy", back_populates="value_chains"
    )
    processes: Mapped[List["Process"]] = relationship(
        "Process",
        back_populates="value_chain",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ValueChain id={self.id} name={self.name!r}>"
