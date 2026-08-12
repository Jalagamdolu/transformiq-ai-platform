"""Scenario Extraction Service.

Orchestrates natural language extraction using LLM providers, with caching
and graceful fallback handling.
"""

from __future__ import annotations

import hashlib
import logging
import re
from typing import Dict, Optional, Tuple
from uuid import UUID

from app.ai.base import BaseLLMProvider, LLMProviderError
from app.ai.prompts.extraction import (
    EXTRACTION_PROMPT_VERSION,
    EXTRACTION_SYSTEM_PROMPT,
    build_extraction_prompt,
)
from app.schemas.scenario import ExtractedScenarioSpec

logger = logging.getLogger(__name__)


class ScenarioExtractionService:
    """Service orchestrating natural language scenario extraction."""

    def __init__(self, provider: BaseLLMProvider) -> None:
        self.provider = provider
        # In-memory cache: cache_key -> ExtractedScenarioSpec
        self._cache: Dict[str, ExtractedScenarioSpec] = {}

    def build_cache_key(self, organisation_id: UUID, user_input: str) -> str:
        """Build cache key incorporating org_id, provider/model, prompt version, and input hash."""
        norm_input = re.sub(r"\s+", " ", user_input.strip().lower())
        raw_key = (
            f"{organisation_id}:{self.provider.provider_name}:"
            f"{self.provider.model_name}:{EXTRACTION_PROMPT_VERSION}:{norm_input}"
        )
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    async def extract_scenario(
        self,
        organisation_id: UUID,
        user_input: str,
        force_refresh: bool = False,
    ) -> Tuple[ExtractedScenarioSpec, bool]:
        """Extract structured scenario from natural language.

        Returns:
            Tuple of (ExtractedScenarioSpec, ai_enhancement_failed_boolean)
        """
        cache_key = self.build_cache_key(organisation_id, user_input)

        if not force_refresh and cache_key in self._cache:
            logger.info("Returning cached scenario extraction for key %s", cache_key[:8])
            return self._cache[cache_key], False

        prompt = build_extraction_prompt(user_input)

        try:
            extracted = await self.provider.generate_structured(
                prompt=prompt,
                response_model=ExtractedScenarioSpec,
                system_prompt=EXTRACTION_SYSTEM_PROMPT,
                temperature=0.0,
            )
            self._cache[cache_key] = extracted
            return extracted, False

        except LLMProviderError as exc:
            logger.warning(
                "LLM extraction failed (%s). Executing deterministic fallback extraction.",
                exc,
            )
            fallback = self._generate_fallback_extraction(user_input)
            return fallback, True

    @staticmethod
    def _generate_fallback_extraction(user_input: str) -> ExtractedScenarioSpec:
        """Deterministic fallback when LLM is unavailable or output fails validation."""
        clean_input = user_input.strip()
        first_line = clean_input.split(".")[0][:80]
        title = first_line if len(first_line) >= 5 else "Custom Transformation Initiative"

        return ExtractedScenarioSpec(
            title=title,
            description=clean_input,
            business_domain="General Operations",
            transformation_type="automation",
            candidate_process_names=[],
            candidate_value_chains=[],
            candidate_ai_opportunity_category="automation",
            candidate_roles=[],
            candidate_skills=[],
            llm_extraction_confidence=0.5,
            assumptions=["LLM service unavailable; generated via deterministic fallback."],
        )
