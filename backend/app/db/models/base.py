"""SQLAlchemy declarative base and reusable mixins.

All ORM models must inherit from `Base`.
Models that need created_at / updated_at should also inherit from `TimestampMixin`.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Project-wide SQLAlchemy declarative base.

    All ORM models inherit from this class.  Alembic reads `Base.metadata`
    to generate migrations.
    """

    pass


class TimestampMixin:
    """Adds `created_at` and `updated_at` columns to any ORM model.

    Timestamps are stored with timezone info and managed by the database.
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class UUIDMixin:
    """Adds a UUID primary key to any ORM model.

    Using UUID PKs makes future multi-tenancy and data exports safer
    (no integer ID collisions across environments).
    """

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        server_default=func.gen_random_uuid(),
    )
