"""Ollama local LLM provider implementation.

Connects to local Ollama instance (http://localhost:11434) using HTTP JSON mode.
"""

from __future__ import annotations

import logging
from typing import Optional, Type, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from app.ai.base import (
    BaseLLMProvider,
    LLMProviderError,
    LLMTimeoutError,
    LLMValidationError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)


class OllamaProvider(BaseLLMProvider):
    """Ollama local LLM provider implementation."""

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "llama3.1",
        timeout: float = 30.0,
    ) -> None:
        super().__init__(provider_name="ollama", model_name=model_name)
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate_structured(
        self,
        prompt: str,
        response_model: Type[T],
        system_prompt: Optional[str] = None,
        temperature: float = 0.0,
    ) -> T:
        """Call Ollama chat endpoint requesting JSON format and validate with Pydantic."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "format": "json",
            "options": {
                "temperature": temperature,
            },
        }

        url = f"{self.base_url}/api/chat"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
        except httpx.TimeoutException as exc:
            logger.error("Ollama request timed out after %s seconds", self.timeout)
            raise LLMTimeoutError(f"Ollama request timed out: {exc}") from exc
        except httpx.HTTPError as exc:
            logger.error("Ollama HTTP request failed: %s", exc)
            raise LLMProviderError(f"Ollama connection error: {exc}") from exc

        content = data.get("message", {}).get("content", "")
        if not content:
            raise LLMProviderError("Ollama returned an empty response")

        try:
            return response_model.model_validate_json(content)
        except ValidationError as exc:
            logger.error("Ollama JSON output failed validation: %s\nContent: %s", exc, content)
            raise LLMValidationError(f"Invalid JSON structure from Ollama: {exc}") from exc

    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
    ) -> str:
        """Call Ollama chat endpoint for free-form text output."""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        payload = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            },
        }

        url = f"{self.base_url}/api/chat"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(url, json=payload)
                resp.raise_for_status()
                data = resp.json()
                return data.get("message", {}).get("content", "")
        except Exception as exc:
            raise LLMProviderError(f"Ollama error: {exc}") from exc
