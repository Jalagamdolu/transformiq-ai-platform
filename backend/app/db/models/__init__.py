"""Database models package.

Importing every model here ensures Alembic's autogenerate can discover all
tables and that SQLAlchemy's mapper registry is fully populated before any
query is executed.
"""

# Base must be first — defines metadata
from app.db.models.base import Base  # noqa: F401

# Association tables — no ORM models, just Table objects
from app.db.models.associations import (  # noqa: F401
    activity_roles,
    activity_skills,
    opportunity_initiatives,
    opportunity_roles,
    opportunity_skills,
)

# Root entity (no FKs to other domain models)
from app.db.models.organisation import Organisation  # noqa: F401

# Level 1 — depend on Organisation only
from app.db.models.role import Role  # noqa: F401
from app.db.models.skill import Skill  # noqa: F401
from app.db.models.strategy import Strategy  # noqa: F401
from app.db.models.transformation_initiative import TransformationInitiative  # noqa: F401

# Level 2 — depend on Strategy/Organisation
from app.db.models.value_chain import ValueChain  # noqa: F401

# Level 3 — depend on ValueChain/Organisation
from app.db.models.process import Process  # noqa: F401

# Level 4 — depend on Process
from app.db.models.activity import Activity  # noqa: F401
from app.db.models.ai_opportunity import AIOpportunity  # noqa: F401

# Level 5 — depend on AIOpportunity
from app.db.models.governance import Governance  # noqa: F401

# Polymorphic (no strict FK to domain entities — intentional)
from app.db.models.dependency import Dependency  # noqa: F401

# Phase 3 — Analysis results
from app.db.models.transformation_analysis import TransformationAnalysis  # noqa: F401

# Phase 4B — Research RAG & Enterprise Semantic Embeddings
from app.db.models.research_source import ResearchSource  # noqa: F401
from app.db.models.document_chunk import DocumentChunk  # noqa: F401
from app.db.models.enterprise_embedding import EnterpriseEntityEmbedding  # noqa: F401

__all__ = [
    "Base",
    # Association tables
    "activity_roles",
    "activity_skills",
    "opportunity_roles",
    "opportunity_skills",
    "opportunity_initiatives",
    # Domain models
    "Organisation",
    "Strategy",
    "ValueChain",
    "Process",
    "Activity",
    "AIOpportunity",
    "Role",
    "Skill",
    "Governance",
    "TransformationInitiative",
    "Dependency",
    "TransformationAnalysis",
    "ResearchSource",
    "DocumentChunk",
    "EnterpriseEntityEmbedding",
]
