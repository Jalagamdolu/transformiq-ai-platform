"""EnterpriseEntityEmbedding ORM model for enterprise semantic retrieval."""

from __future__ import annotations

import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Column, ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, relationship

from app.db.models.base import Base, TimestampMixin, UUIDMixin


class EnterpriseEntityEmbedding(Base, UUIDMixin, TimestampMixin):
    """Stores pgvector embeddings of enterprise entities for semantic search.

    Tracks content_hash and embedding metadata for stale embedding detection.
    """

    __tablename__ = "enterprise_entity_embeddings"

    organisation_id = Column(
        PG_UUID(as_uuid=True),
        ForeignKey("organisations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    entity_type = Column(String(50), nullable=False, index=True)  # process, opportunity, value_chain, role, skill
    entity_id = Column(PG_UUID(as_uuid=True), nullable=False, index=True)
    searchable_text = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, index=True)
    embedding_model = Column(String(100), nullable=False, default="all-MiniLM-L6-v2")
    embedding_model_version = Column(String(20), nullable=False, default="1.0.0")
    embedding = Column(Vector(384), nullable=False)
