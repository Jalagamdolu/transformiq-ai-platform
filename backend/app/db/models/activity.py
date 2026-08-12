"""Activity model."""

from __future__ import annotations

import uuid
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models.associations import activity_roles, activity_skills
from app.db.models.base import Base, TimestampMixin, UUIDMixin

if TYPE_CHECKING:
    from app.db.models.process import Process
    from app.db.models.role import Role
    from app.db.models.skill import Skill


class Activity(Base, UUIDMixin, TimestampMixin):
    """A discrete step within a business process."""

    __tablename__ = "activities"

    process_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("processes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # manual | automated | decision | review
    activity_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    # active | inactive
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="active"
    )
    # Optional ordering within the process
    sequence_order: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # ── Relationships ─────────────────────────────────────────────────────── #
    process: Mapped["Process"] = relationship("Process", back_populates="activities")
    roles: Mapped[List["Role"]] = relationship(
        "Role", secondary=activity_roles, back_populates="activities"
    )
    skills: Mapped[List["Skill"]] = relationship(
        "Skill", secondary=activity_skills, back_populates="activities"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Activity id={self.id} name={self.name!r}>"
