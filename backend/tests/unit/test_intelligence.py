"""Unit tests for Phase 5 Backend Intelligence Services and Analyst Intent Router."""

import pytest
from app.ai.analyst import ExecutiveAnalystIntent, ExecutiveAnalystService
from app.db.session import AsyncSessionLocal
from app.services.intelligence_service import (
    DependencyIntelligenceService,
    GovernanceIntelligenceService,
    PriorityIntelligenceService,
    SkillIntelligenceService,
)


def test_analyst_intent_classification():
    async_session = AsyncSessionLocal()
    analyst = ExecutiveAnalystService(async_session)

    intent1, conf1 = analyst.classify_intent("What should we transform first?")
    assert intent1 == ExecutiveAnalystIntent.PRIORITY_RANKING
    assert conf1 > 0.90

    intent2, conf2 = analyst.classify_intent("Which processes have the greatest AI opportunity?")
    assert intent2 == ExecutiveAnalystIntent.PROCESS_INTELLIGENCE

    intent3, conf3 = analyst.classify_intent("Which roles will change most?")
    assert intent3 == ExecutiveAnalystIntent.ROLE_IMPACT

    intent4, conf4 = analyst.classify_intent("What skills should we invest in?")
    assert intent4 == ExecutiveAnalystIntent.SKILL_INVESTMENT

    intent5, conf5 = analyst.classify_intent("What are our highest governance risks?")
    assert intent5 == ExecutiveAnalystIntent.GOVERNANCE_RISK

    intent6, conf6 = analyst.classify_intent("What dependencies could prevent transformation?")
    assert intent6 == ExecutiveAnalystIntent.DEPENDENCY_BLOCKERS


@pytest.mark.asyncio
async def test_priority_intelligence_service_deduplication():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.db.models import Organisation
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()
        assert org is not None

        priority_service = PriorityIntelligenceService(session)
        result = await priority_service.get_ranked_priorities(org.id)

        assert result["total_opportunities"] == 8
        assert result["total_unique_priorities"] > 0
        assert result["total_analyses_history"] >= result["total_unique_priorities"]
        assert isinstance(result["items"], list)

        # Verify no duplicate titles exist in returned priority items
        titles = [item["title"] for item in result["items"]]
        assert len(titles) == len(set(titles)), "Priority items list must not contain duplicate titles."

        # Verify top priority score remains 86.2
        assert abs(result["items"][0]["priority_score"] - 86.2) < 0.1


@pytest.mark.asyncio
async def test_governance_intelligence_service():
    async with AsyncSessionLocal() as session:
        from sqlalchemy import select
        from app.db.models import Organisation
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()
        assert org is not None

        gov_service = GovernanceIntelligenceService(session)
        result = await gov_service.get_governance_portfolio(org.id)

        assert "total_risk_records" in result
        assert "findings" in result
