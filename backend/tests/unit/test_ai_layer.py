"""Unit tests for Phase 4A AI layer (Providers, Services, Caching, Fallbacks)."""

import uuid
import pytest
from pydantic import BaseModel, ValidationError

from app.ai.base import LLMProviderError, LLMTimeoutError, LLMValidationError
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.factory import get_llm_provider
from app.ai.services.extraction_service import ScenarioExtractionService
from app.ai.services.explanation_service import ExecutiveExplanationService
from app.schemas.scenario import ExtractedScenarioSpec, ExecutiveExplanation


@pytest.mark.asyncio
async def test_mock_provider_structured_extraction():
    provider = MockLLMProvider()
    spec = await provider.generate_structured(
        prompt="Introduce AI supplier risk assessment",
        response_model=ExtractedScenarioSpec,
    )
    assert spec.title == "AI-Powered Supplier Risk Assessment"
    assert spec.llm_extraction_confidence == 0.92
    assert "Supply Chain Analyst" in spec.candidate_roles


@pytest.mark.asyncio
async def test_mock_provider_timeout_error():
    provider = MockLLMProvider(should_timeout=True)
    with pytest.raises(LLMTimeoutError):
        await provider.generate_structured(
            prompt="Test prompt",
            response_model=ExtractedScenarioSpec,
        )


@pytest.mark.asyncio
async def test_mock_provider_validation_error():
    provider = MockLLMProvider(should_fail_validation=True)
    with pytest.raises(LLMValidationError):
        await provider.generate_structured(
            prompt="Test prompt",
            response_model=ExtractedScenarioSpec,
        )


@pytest.mark.asyncio
async def test_extraction_service_caching():
    provider = MockLLMProvider()
    service = ScenarioExtractionService(provider)
    org_id = uuid.uuid4()
    text = "Supplier risk evaluation scenario"

    # First call - cache miss
    spec1, failed1 = await service.extract_scenario(org_id, text, force_refresh=False)
    assert not failed1

    # Key generation check
    key = service.build_cache_key(org_id, text)
    assert key in service._cache

    # Second call - cache hit
    spec2, failed2 = await service.extract_scenario(org_id, text, force_refresh=False)
    assert not failed2
    assert spec1 == spec2

    # Force refresh - bypass cache
    spec3, failed3 = await service.extract_scenario(org_id, text, force_refresh=True)
    assert not failed3


@pytest.mark.asyncio
async def test_extraction_service_fallback_on_llm_failure():
    provider = MockLLMProvider(should_fail=True)
    service = ScenarioExtractionService(provider)
    org_id = uuid.uuid4()

    fallback_spec, failed = await service.extract_scenario(org_id, "Critical supply chain automation")
    assert failed is True
    assert fallback_spec.llm_extraction_confidence == 0.5
    assert "fallback" in fallback_spec.assumptions[0].lower()


@pytest.mark.asyncio
async def test_explanation_service_generation_and_fallback():
    # Success
    provider = MockLLMProvider()
    service = ExecutiveExplanationService(provider)
    mock_analysis = {"title": "Test Initiative", "priority_score": 85.0, "priority_category": "HIGH"}
    explanation = await service.generate_explanation(mock_analysis)
    assert "priority score" in explanation.executive_summary.lower()

    # Fallback on LLM failure
    fail_provider = MockLLMProvider(should_fail=True)
    fail_service = ExecutiveExplanationService(fail_provider)
    fallback_exp = await fail_service.generate_explanation(mock_analysis)
    assert fallback_exp.executive_summary.startswith("Transformation scenario 'Test Initiative'")
