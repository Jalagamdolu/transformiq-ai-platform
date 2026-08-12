"""TransformationAnalysis model — stores structured results of intelligence engine analysis."""

from __future__ import annotations

import uuid
from typing import Any, Dict, Optional

from sqlalchemy import Float, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class TransformationAnalysis(Base, UUIDMixin, TimestampMixin):
    """Stores persistent results of a transformation intelligence analysis."""

    __tablename__ = "transformation_analyses"

    organisation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # completed | pending | failed
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="completed", index=True
    )

    # Optional bindings to known enterprise entities
    opportunity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("ai_opportunities.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    process_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    strategy_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("strategies.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Deterministic priority score and rating
    priority_score: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    # HIGH | MEDIUM | LOW
    priority_category: Mapped[str] = mapped_column(
        String(20), nullable=False, default="LOW", index=True
    )

    # Structured JSON payloads
    factor_scores: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    reason_codes: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    affected_entities: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    governance_findings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )
    dependency_findings: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, nullable=False, default=dict
    )

    engine_version: Mapped[str] = mapped_column(
        String(20), nullable=False, default="1.0.0"
    )

    # ── Relationships ─────────────────────────────────────────────────────── #
    organisation: Mapped[Any] = relationship("Organisation")
    opportunity: Mapped[Any] = relationship("AIOpportunity")
    process: Mapped[Any] = relationship("Process")
    strategy: Mapped[Any] = relationship("Strategy")

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<TransformationAnalysis id={self.id} title={self.title!r} "
            f"score={self.priority_score:.1f} ({self.priority_category})>"
        )
