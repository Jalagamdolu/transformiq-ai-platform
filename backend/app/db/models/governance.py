"""Governance model — AI transformation risk and compliance records."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, Optional

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.ai_opportunity import AIOpportunity


class Governance(Base, UUIDMixin, TimestampMixin):
    """A governance / risk record for a specific AI opportunity.

    One record per (opportunity, category) — e.g. one privacy record, one
    bias/fairness record, etc.  The unique constraint is intentionally relaxed
    so multiple notes per category are allowed for richer documentation.
    """

    __tablename__ = "governance"

    ai_opportunity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_opportunities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    # privacy | security | bias_fairness | explainability | human_oversight
    # | model_risk | compliance | monitoring
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # low | medium | high | critical
    risk_level: Mapped[str] = mapped_column(
        String(20), nullable=False, default="medium"
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    ai_opportunity: Mapped["AIOpportunity"] = relationship(
        "AIOpportunity", back_populates="governance_records"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<Governance id={self.id} category={self.category!r} "
            f"risk={self.risk_level!r}>"
        )
