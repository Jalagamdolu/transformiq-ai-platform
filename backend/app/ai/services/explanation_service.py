"""Executive Explanation Service.

Synthesizes structured C-suite executive briefings from Phase 3 deterministic analysis results.
"""

from __future__ import annotations

import logging
from typing import Dict

from app.ai.base import BaseLLMProvider, LLMProviderError
from app.ai.prompts.explanation import (
    EXPLANATION_SYSTEM_PROMPT,
    build_explanation_prompt,
)
from app.schemas.scenario import ExecutiveExplanation

logger = logging.getLogger(__name__)


class ExecutiveExplanationService:
    """Service generating executive explanations from deterministic analysis."""

    def __init__(self, provider: BaseLLMProvider) -> None:
        self.provider = provider

    async def generate_explanation(
        self,
        analysis_dict: Dict,
    ) -> ExecutiveExplanation:
        """Synthesize executive briefing from Phase 3 analysis JSON.

        Returns:
            ExecutiveExplanation Pydantic model instance.
        """
        prompt = build_explanation_prompt(analysis_dict)

        try:
            return await self.provider.generate_structured(
                prompt=prompt,
                response_model=ExecutiveExplanation,
                system_prompt=EXPLANATION_SYSTEM_PROMPT,
                temperature=0.2,
            )
        except LLMProviderError as exc:
            logger.warning(
                "LLM explanation synthesis failed (%s). Generating template fallback briefing.",
                exc,
            )
            return self._generate_fallback_explanation(analysis_dict)

    @staticmethod
    def _generate_fallback_explanation(analysis_dict: Dict) -> ExecutiveExplanation:
        """Deterministic template fallback when LLM is unavailable."""
        title = analysis_dict.get("title", "Transformation Scenario")
        score = analysis_dict.get("priority_score", 0.0)
        category = analysis_dict.get("priority_category", "LOW")
        affected = analysis_dict.get("affected_entities", {})

        processes = [p["name"] for p in affected.get("processes", [])]
        roles = [r["name"] for r in affected.get("roles", [])]
        skills = [s["name"] for s in affected.get("skills", [])]
        govs = [g.get("description", "") for g in analysis_dict.get("governance_findings", [])]

        return ExecutiveExplanation(
            executive_summary=(
                f"Transformation scenario '{title}' evaluated with a Priority Score of {score:.1f}/100 "
                f"({category} Priority). Analysis completed via deterministic engine."
            ),
            strategic_rationale=(
                f"Priority score driven by strategic alignment and business value across "
                f"{len(processes)} processes and {len(roles)} enterprise roles."
            ),
            key_impacted_areas=[
                f"Impacted Processes: {', '.join(processes) if processes else 'General Operations'}",
                f"Impacted Roles: {', '.join(roles) if roles else 'Standard Workforce'}",
                f"Required Skills: {', '.join(skills) if skills else 'General Skills'}",
            ],
            risk_and_governance_advice=govs if govs else [
                "Verify privacy and data governance compliance prior to implementation."
            ],
            recommended_next_steps=[
                "Review Phase 3 factor score details with department stakeholders.",
                "Initiate pilot planning and resource allocation.",
            ],
        )
