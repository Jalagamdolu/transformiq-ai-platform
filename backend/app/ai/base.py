"""Base interface and exceptions for LLM model providers.

Supports structured output generation adhering to Pydantic schemas.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LLMProviderError(Exception):
    """Base exception for LLM provider errors."""

    pass


class LLMTimeoutError(LLMProviderError):
    """Raised when an LLM call times out."""

    pass


class LLMValidationError(LLMProviderError):
    """Raised when LLM output fails Pydantic schema validation."""

    pass


class BaseLLMProvider(ABC):
    """Abstract Base Class for LLM model providers (Ollama, OpenAI, Mock, etc.)."""

    def __init__(self, provider_name: str, model_name: str) -> None:
        self.provider_name = provider_name
        self.model_name = model_name

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> T:
        """Generate structured output validated against response_model.

        Args:
            prompt: User prompt input string.
            response_model: Pydantic model class to validate model JSON against.
            system_prompt: Optional system prompt instructions.
            temperature: Model sampling temperature (0.0 = deterministic).

        Returns:
            Validated Pydantic model instance.
        """
        pass

    @abstractmethod
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate free-form text output.

        Args:
            prompt: User prompt input string.
            system_prompt: Optional system prompt instructions.
            temperature: Model sampling temperature.

        Returns:
            Generated text string.
        """
        pass
