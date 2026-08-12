"""Provider factory for LLM model instances.

Instantiates appropriate provider based on configuration settings or test overrides.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.ai.base import BaseLLMProvider
from app.ai.providers.mock import MockLLMProvider
from app.ai.providers.ollama import OllamaProvider
from app.core.config import settings

logger = logging.getLogger(__name__)


def get_llm_provider(
    provider_name: Optional[str] = None,
    model_name: Optional[str] = None,
) -> BaseLLMProvider:
    """Factory function to resolve and instantiate an LLM provider.

    Default settings (or environment == 'testing') route to MockLLMProvider or OllamaProvider.
    """
    selected_provider = (provider_name or settings.llm_provider).lower()
    selected_model = model_name or settings.llm_model

    # In testing environment or when mock explicitly requested, return MockLLMProvider
    if settings.environment.lower() == "testing" or selected_provider == "mock":
        return MockLLMProvider(model_name=selected_model)

    if selected_provider == "ollama":
        return OllamaProvider(
            base_url=settings.llm_base_url,
            model_name=selected_model,
        )

    # Fallback to MockLLMProvider with warning if unknown provider requested
    logger.warning("Unknown LLM provider '%s' requested; falling back to MockLLMProvider", selected_provider)
    return MockLLMProvider(model_name=selected_model)
