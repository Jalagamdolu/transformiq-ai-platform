"""Mock LLM provider implementation for testing.

Provides deterministic responses adhering to Pydantic response models
without requiring a network connection or running LLM service.
"""

from __future__ import annotations

import logging
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

from app.ai.base import BaseLLMProvider, LLMValidationError
from app.schemas.scenario import ExecutiveExplanation, ExtractedScenarioSpec

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class MockLLMProvider(BaseLLMProvider):
    """Mock LLM provider returning realistic structured test fixtures."""

    def __init__(
        self,
        model_name: str = "mock-model-v1",
        should_fail: bool = False,
        should_timeout: bool = False,
        should_fail_validation: bool = False,
    ) -> None:
        super().__init__(provider_name="mock", model_name=model_name)
        self.should_fail = should_fail
        self.should_timeout = should_timeout
        self.should_fail_validation = should_fail_validation

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> T:
        """Return pre-built mock fixture instances matching response_model."""
        if self.should_timeout:
            from app.ai.base import LLMTimeoutError
            raise LLMTimeoutError("Mock provider simulated timeout")

        if self.should_fail:
            from app.ai.base import LLMProviderError
            raise LLMProviderError("Mock provider simulated connection failure")

        if self.should_fail_validation:
            raise LLMValidationError("Mock provider simulated Pydantic schema validation error")

        if response_model == ExtractedScenarioSpec:
            # Check for supplier risk assessment scenario keywords in prompt
            if "supplier risk" in prompt.lower() or "supplier" in prompt.lower():
                return ExtractedScenarioSpec(
                    title="AI-Powered Supplier Risk Assessment",
                    description="Deploying AI models to assess supplier risk, track lead times, and evaluate vendor compliance.",
                    business_domain="Supply Chain Operations",
                    transformation_type="automation",
                    candidate_process_names=["Supplier Order Fulfillment", "Demand Forecasting"],
                    candidate_value_chains=["Supply Chain & Merchandising"],
                    candidate_ai_opportunity_category="analytics",
                    candidate_roles=["Supply Chain Analyst", "Demand Planner"],
                    candidate_skills=["Supply Chain Analytics", "Data Analysis"],
                    llm_extraction_confidence=0.92,
                    assumptions=["Assumes historical supplier ASN lead times are available."],
                ) # type: ignore

            if "slotting" in prompt.lower() or "warehouse" in prompt.lower():
                return ExtractedScenarioSpec(
                    title="AI-Powered Warehouse Slotting Optimisation",
                    description="Optimizing warehouse slotting layouts for fast-moving retail SKUs using predictive machine learning.",
                    business_domain="Warehouse & Logistics",
                    transformation_type="optimization",
                    candidate_process_names=["Warehouse Slotting Layout Optimization"],
                    candidate_value_chains=["Supply Chain & Merchandising"],
                    candidate_ai_opportunity_category="optimization",
                    candidate_roles=["Inventory Controller", "Store Manager"],
                    candidate_skills=["Inventory Optimization"],
                    llm_extraction_confidence=0.90,
                    assumptions=["Assumes historical SKU picking frequency data is available."],
                ) # type: ignore

            if "workforce" in prompt.lower() or "scheduling" in prompt.lower():
                return ExtractedScenarioSpec(
                    title="AI-Assisted Workforce Scheduling",
                    description="Automating store staff shift scheduling and labor budget optimization using foot-traffic predictions.",
                    business_domain="Store Operations",
                    transformation_type="augmentation",
                    candidate_process_names=["Workforce Scheduling"],
                    candidate_value_chains=["Store & Digital Operations"],
                    candidate_ai_opportunity_category="augmentation",
                    candidate_roles=["Store Manager", "Shift Supervisor"],
                    candidate_skills=["Workforce Management", "Labor Optimization"],
                    llm_extraction_confidence=0.91,
                    assumptions=["Assumes POS foot-traffic data is available."],
                ) # type: ignore

            # Generic fallback mock extraction
            return ExtractedScenarioSpec(
                title="Extracted Transformation Initiative",
                description="Natural language extracted transformation scenario for enterprise processing.",
                business_domain="Enterprise Operations",
                transformation_type="automation",
                candidate_process_names=["Demand Forecasting"],
                candidate_value_chains=["Supply Chain & Merchandising"],
                candidate_ai_opportunity_category="automation",
                candidate_roles=["Supply Chain Analyst"],
                candidate_skills=["Data Analysis"],
                llm_extraction_confidence=0.88,
                assumptions=["Assumes standard enterprise data availability."],
            ) # type: ignore

        if response_model == ExecutiveExplanation:
            return ExecutiveExplanation(
                executive_summary="The proposed initiative achieves a high priority score driven by strong alignment with core supply chain initiatives and high business value.",
                strategic_rationale="Aligns directly with the Enterprise AI Supply Chain Modernization initiative and core operational value chains.",
                key_impacted_areas=[
                    "Processes: Supplier Order Fulfillment, Demand Forecasting",
                    "Roles: Supply Chain Analyst, Demand Planner",
                    "Skills: Supply Chain Analytics, Data Analysis",
                ],
                risk_and_governance_advice=[
                    "Ensure vendor data privacy constraints are audited.",
                    "Implement human-in-the-loop review for critical supplier decisions.",
                ],
                recommended_next_steps=[
                    "Approve pilot deployment for high-volume vendors.",
                    "Establish feature explainability dashboards for planners.",
                ],
            ) # type: ignore

        # Fallback for arbitrary BaseModel
        return response_model.model_construct()

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Return simple mock text."""
        return "Mock LLM narrative executive summary response."
