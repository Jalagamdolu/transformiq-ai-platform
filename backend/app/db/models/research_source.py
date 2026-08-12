"""ResearchSource ORM model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, Date, ForeignKey, String, Text, DateTime
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.sql import func

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.document_chunk import DocumentChunk
    from app.db.models.organisation import Organisation


class ResearchSource(Base, UUIDMixin, TimestampMixin):
    """Research source metadata model."""

    __tablename__ = "research_sources"

    organisation_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    title = Column(String(512), nullable=False)
    publisher = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    source_type = Column(String(50), nullable=False, default="industry_report")
    publication_date = Column(Date, nullable=True)
    retrieved_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    content_hash = Column(String(64), nullable=False, unique=True, index=True)
    credibility_metadata = Column(JSONB, nullable=False, server_default="{}")

    # Relationships
    organisation: Mapped[Optional[Organisation]] = relationship("Organisation")
    chunks: Mapped[List[DocumentChunk]] = relationship(
        "DocumentChunk",
        back_populates="source",
        cascade="all, delete-orphan",
    )
