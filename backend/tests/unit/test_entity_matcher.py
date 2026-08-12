"""Unit tests for EntityMatcher Tier 1 and Tier 2 matching."""

import uuid
import pytest
from app.db.session import AsyncSessionLocal
from app.engines.entity_matcher import EntityMatcher
from app.schemas.scenario import ExtractedScenarioSpec


@pytest.mark.asyncio
async def test_entity_matcher_exact_and_fuzzy():
    async with AsyncSessionLocal() as session:
        matcher = EntityMatcher(session)
        
        # Get NovaMart org ID
        from sqlalchemy import select
        from app.db.models import Organisation
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()
        assert org is not None

        # Test exact/fuzzy matching for Demand Forecasting
        extracted = ExtractedScenarioSpec(
            title="AI-Powered Demand Forecasting",
            description="Predicting store SKU demand using machine learning",
            business_domain="Supply Chain",
            transformation_type="automation",
            candidate_process_names=["Demand Forecasting"],
            candidate_value_chains=["Supply Chain & Merchandising"],
            candidate_ai_opportunity_category="automation",
            candidate_roles=["Demand Planner"],
            candidate_skills=["Demand Forecasting"],
            llm_extraction_confidence=0.9,
            assumptions=[],
        )

        matched = await matcher.match_extracted_concepts(org.id, extracted)
        assert matched.process_match.entity_name == "Demand Forecasting"
        assert matched.process_match.match_confidence >= 0.85
        assert matched.opportunity_match.entity_name == "AI-Powered Demand Forecasting"
        assert matched.matched_entity_count >= 2


@pytest.mark.asyncio
async def test_entity_matcher_no_match_thresholding():
    async with AsyncSessionLocal() as session:
        matcher = EntityMatcher(session)
        
        from sqlalchemy import select
        from app.db.models import Organisation
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()

        # Input with non-existent concepts
        extracted = ExtractedScenarioSpec(
            title="Quantum Blockchain Space Exploration",
            description="Deploying orbital satellite communications",
            business_domain="Aerospace",
            transformation_type="automation",
            candidate_process_names=["Zero Gravity Manufacturing"],
            candidate_value_chains=["Intergalactic Shipping"],
            candidate_ai_opportunity_category="automation",
            candidate_roles=["Astronaut"],
            candidate_skills=["Orbital Dynamics"],
            llm_extraction_confidence=0.9,
            assumptions=[],
        )

        matched = await matcher.match_extracted_concepts(org.id, extracted)
        assert matched.process_match.entity_id is None
        assert matched.process_match.match_method == "none"
        assert matched.process_match.match_confidence == 0.0
        assert matched.matched_entity_count == 0
