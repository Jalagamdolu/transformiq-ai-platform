"""Integration tests for seed data verification."""

import pytest
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.db.models import (
    Organisation,
    Strategy,
    ValueChain,
    Process,
    Activity,
    AIOpportunity,
    Role,
    Skill,
    TransformationInitiative,
    Dependency,
)
from app.db.models.associations import (
    activity_roles,
    activity_skills,
    opportunity_roles,
    opportunity_skills,
)


@pytest.mark.asyncio
async def test_novamart_seed_data_persisted():
    """Verify that NovaMart synthetic data exists in PostgreSQL database."""
    async with AsyncSessionLocal() as session:
        # Organisation
        res = await session.execute(
            select(Organisation).where(Organisation.name == "NovaMart")
        )
        org = res.scalar_one_or_none()
        assert org is not None, "NovaMart organisation not found in DB"
        assert org.industry == "Retail"

        # Strategies
        res = await session.execute(
            select(Strategy).where(Strategy.organisation_id == org.id)
        )
        strategies = res.scalars().all()
        assert len(strategies) >= 3

        # Value Chains
        res = await session.execute(
            select(ValueChain).where(ValueChain.organisation_id == org.id)
        )
        value_chains = res.scalars().all()
        assert len(value_chains) >= 4

        # Processes
        res = await session.execute(
            select(Process).where(Process.organisation_id == org.id)
        )
        processes = res.scalars().all()
        assert len(processes) >= 10

        # Activities
        res = await session.execute(select(Activity))
        activities = res.scalars().all()
        assert len(activities) >= 20

        # Roles & Skills
        res = await session.execute(select(Role).where(Role.organisation_id == org.id))
        roles = res.scalars().all()
        assert len(roles) >= 8

        res = await session.execute(select(Skill).where(Skill.organisation_id == org.id))
        skills = res.scalars().all()
        assert len(skills) >= 10

        # AI Opportunities
        res = await session.execute(
            select(AIOpportunity).where(AIOpportunity.organisation_id == org.id)
        )
        opportunities = res.scalars().all()
        assert len(opportunities) >= 8

        # Transformation Initiatives
        res = await session.execute(
            select(TransformationInitiative).where(
                TransformationInitiative.organisation_id == org.id
            )
        )
        initiatives = res.scalars().all()
        assert len(initiatives) >= 3

        # Dependencies
        res = await session.execute(
            select(Dependency).where(Dependency.organisation_id == org.id)
        )
        dependencies = res.scalars().all()
        assert len(dependencies) >= 3

        # ── Phase 3.1 Verification: Association tables populated ─────────────── #
        act_roles_count = (await session.execute(select(func.count()).select_from(activity_roles))).scalar_one()
        assert act_roles_count > 0, "activity_roles association table is empty!"

        act_skills_count = (await session.execute(select(func.count()).select_from(activity_skills))).scalar_one()
        assert act_skills_count > 0, "activity_skills association table is empty!"

        opp_roles_count = (await session.execute(select(func.count()).select_from(opportunity_roles))).scalar_one()
        assert opp_roles_count > 0, "opportunity_roles association table is empty!"

        opp_skills_count = (await session.execute(select(func.count()).select_from(opportunity_skills))).scalar_one()
        assert opp_skills_count > 0, "opportunity_skills association table is empty!"
