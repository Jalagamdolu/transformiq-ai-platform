"""Association tables for many-to-many relationships.

These are pure SQLAlchemy Table objects (not ORM classes) so they can be
imported by any model file without causing circular imports.
"""

from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.models.base import Base

# ---------------------------------------------------------------------------
# Activity ↔ Role
# ---------------------------------------------------------------------------
activity_roles = Table(
    "activity_roles",
    Base.metadata,
    Column(
        "activity_id",
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# ---------------------------------------------------------------------------
# Activity ↔ Skill
# ---------------------------------------------------------------------------
activity_skills = Table(
    "activity_skills",
    Base.metadata,
    Column(
        "activity_id",
        UUID(as_uuid=True),
        ForeignKey("activities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# ---------------------------------------------------------------------------
# AIOpportunity ↔ Role
# ---------------------------------------------------------------------------
opportunity_roles = Table(
    "opportunity_roles",
    Base.metadata,
    Column(
        "opportunity_id",
        UUID(as_uuid=True),
        ForeignKey("ai_opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        UUID(as_uuid=True),
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# ---------------------------------------------------------------------------
# AIOpportunity ↔ Skill
# ---------------------------------------------------------------------------
opportunity_skills = Table(
    "opportunity_skills",
    Base.metadata,
    Column(
        "opportunity_id",
        UUID(as_uuid=True),
        ForeignKey("ai_opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "skill_id",
        UUID(as_uuid=True),
        ForeignKey("skills.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)

# ---------------------------------------------------------------------------
# AIOpportunity ↔ TransformationInitiative
# ---------------------------------------------------------------------------
opportunity_initiatives = Table(
    "opportunity_initiatives",
    Base.metadata,
    Column(
        "opportunity_id",
        UUID(as_uuid=True),
        ForeignKey("ai_opportunities.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "initiative_id",
        UUID(as_uuid=True),
        ForeignKey("transformation_initiatives.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)
