"""Enterprise domain tables.

Revision ID: 0002
Revises: 0001
Create Date: 2026-08-12

Creates all 11 domain tables and 5 association tables for Phase 2:
- organisations
- strategies
- value_chains
- roles
- skills
- processes
- activities
- ai_opportunities
- governance
- transformation_initiatives
- dependencies
- association tables (activity_roles, activity_skills, opportunity_roles, opportunity_skills, opportunity_initiatives)
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "0002"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. organisations
    op.create_table(
        "organisations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("industry", sa.String(100), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_organisations_name", "organisations", ["name"])

    # 2. strategies
    op.create_table(
        "strategies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("time_horizon", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("organisation_id", "name", name="uq_strategy_org_name"),
    )
    op.create_index("ix_strategies_organisation_id", "strategies", ["organisation_id"])
    op.create_index("ix_strategies_name", "strategies", ["name"])
    op.create_index("ix_strategies_status", "strategies", ["status"])

    # 3. value_chains
    op.create_table(
        "value_chains",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("strategy_id", "name", name="uq_valuechain_strategy_name"),
    )
    op.create_index("ix_value_chains_organisation_id", "value_chains", ["organisation_id"])
    op.create_index("ix_value_chains_strategy_id", "value_chains", ["strategy_id"])
    op.create_index("ix_value_chains_name", "value_chains", ["name"])

    # 4. roles
    op.create_table(
        "roles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("organisation_id", "name", name="uq_role_org_name"),
    )
    op.create_index("ix_roles_organisation_id", "roles", ["organisation_id"])
    op.create_index("ix_roles_name", "roles", ["name"])

    # 5. skills
    op.create_table(
        "skills",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("skill_type", sa.String(50), nullable=False, server_default="technical"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("organisation_id", "name", name="uq_skill_org_name"),
    )
    op.create_index("ix_skills_organisation_id", "skills", ["organisation_id"])
    op.create_index("ix_skills_name", "skills", ["name"])

    # 6. processes
    op.create_table(
        "processes",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("value_chain_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("value_chains.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("process_type", sa.String(50), nullable=False, server_default="operational"),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.UniqueConstraint("value_chain_id", "name", name="uq_process_vc_name"),
    )
    op.create_index("ix_processes_organisation_id", "processes", ["organisation_id"])
    op.create_index("ix_processes_value_chain_id", "processes", ["value_chain_id"])
    op.create_index("ix_processes_name", "processes", ["name"])
    op.create_index("ix_processes_status", "processes", ["status"])

    # 7. activities
    op.create_table(
        "activities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("activity_type", sa.String(50), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("sequence_order", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_activities_process_id", "activities", ["process_id"])

    # 8. ai_opportunities
    op.create_table(
        "ai_opportunities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("process_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("processes.id", ondelete="SET NULL"), nullable=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=False, server_default="automation"),
        sa.Column("status", sa.String(50), nullable=False, server_default="identified"),
        sa.Column("ai_technology", sa.String(100), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_ai_opportunities_organisation_id", "ai_opportunities", ["organisation_id"])
    op.create_index("ix_ai_opportunities_process_id", "ai_opportunities", ["process_id"])
    op.create_index("ix_ai_opportunities_name", "ai_opportunities", ["name"])
    op.create_index("ix_ai_opportunities_status", "ai_opportunities", ["status"])

    # 9. governance
    op.create_table(
        "governance",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("ai_opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_opportunities.id", ondelete="CASCADE"), nullable=False),
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("risk_level", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_governance_ai_opportunity_id", "governance", ["ai_opportunity_id"])
    op.create_index("ix_governance_category", "governance", ["category"])

    # 10. transformation_initiatives
    op.create_table(
        "transformation_initiatives",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="proposed"),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_transformation_initiatives_organisation_id", "transformation_initiatives", ["organisation_id"])
    op.create_index("ix_transformation_initiatives_name", "transformation_initiatives", ["name"])
    op.create_index("ix_transformation_initiatives_status", "transformation_initiatives", ["status"])

    # 11. dependencies
    op.create_table(
        "dependencies",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("organisation_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("organisations.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_entity_type", sa.String(50), nullable=False),
        sa.Column("source_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_entity_type", sa.String(50), nullable=False),
        sa.Column("target_entity_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relationship_type", sa.String(50), nullable=False, server_default="requires"),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_dependencies_organisation_id", "dependencies", ["organisation_id"])

    # Association tables
    op.create_table(
        "activity_roles",
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "activity_skills",
        sa.Column("activity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("activities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "opportunity_roles",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_opportunities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("role_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "opportunity_skills",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_opportunities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("skill_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("skills.id", ondelete="CASCADE"), primary_key=True),
    )

    op.create_table(
        "opportunity_initiatives",
        sa.Column("opportunity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ai_opportunities.id", ondelete="CASCADE"), primary_key=True),
        sa.Column("initiative_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("transformation_initiatives.id", ondelete="CASCADE"), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table("opportunity_initiatives")
    op.drop_table("opportunity_skills")
    op.drop_table("opportunity_roles")
    op.drop_table("activity_skills")
    op.drop_table("activity_roles")
    op.drop_table("dependencies")
    op.drop_table("transformation_initiatives")
    op.drop_table("governance")
    op.drop_table("ai_opportunities")
    op.drop_table("activities")
    op.drop_table("processes")
    op.drop_table("skills")
    op.drop_table("roles")
    op.drop_table("value_chains")
    op.drop_table("strategies")
    op.drop_table("organisations")
