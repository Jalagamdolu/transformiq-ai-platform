"""Transformation analysis table.

Revision ID: 0003
Revises: 0002
Create Date: 2026-08-12

Creates transformation_analyses table for persisting structured intelligence analysis results.
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "transformation_analyses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column(
            "organisation_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("organisations.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="completed"),
        sa.Column(
            "opportunity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("ai_opportunities.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "process_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("processes.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "strategy_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("strategies.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("priority_score", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("priority_category", sa.String(20), nullable=False, server_default="LOW"),
        sa.Column("factor_scores", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}" ),
        sa.Column("reason_codes", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}" ),
        sa.Column("affected_entities", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}" ),
        sa.Column("governance_findings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}" ),
        sa.Column("dependency_findings", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default="{}" ),
        sa.Column("engine_version", sa.String(20), nullable=False, server_default="1.0.0"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_transformation_analyses_organisation_id", "transformation_analyses", ["organisation_id"])
    op.create_index("ix_transformation_analyses_title", "transformation_analyses", ["title"])
    op.create_index("ix_transformation_analyses_status", "transformation_analyses", ["status"])
    op.create_index("ix_transformation_analyses_opportunity_id", "transformation_analyses", ["opportunity_id"])
    op.create_index("ix_transformation_analyses_process_id", "transformation_analyses", ["process_id"])
    op.create_index("ix_transformation_analyses_strategy_id", "transformation_analyses", ["strategy_id"])
    op.create_index("ix_transformation_analyses_priority_category", "transformation_analyses", ["priority_category"])


def downgrade() -> None:
    op.drop_table("transformation_analyses")
