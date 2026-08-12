"""DocumentChunk ORM model with pgvector 384-dim vector column."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, Integer, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.research_source import ResearchSource


class DocumentChunk(Base, UUIDMixin, TimestampMixin):
    """Document chunk model storing text, metadata, and pgvector embeddings."""

    __tablename__ = "document_chunks"

    source_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("research_sources.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    metadata_json = Column("metadata", JSONB, nullable=False, server_default="{}")
    embedding = Column(Vector(384), nullable=False)

    # Relationship
    source: Mapped[ResearchSource] = relationship("ResearchSource", back_populates="chunks")
