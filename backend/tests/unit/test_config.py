"""Unit tests for application configuration.

These tests verify that Settings loads correctly with all defaults.
No database or network connection is required.
"""

from __future__ import annotations

import pytest

from app.core.config import settings


class TestSettings:
    def test_app_name_is_set(self) -> None:
        assert settings.app_name == "TransformIQ API"

    def test_app_version_is_set(self) -> None:
        assert settings.app_version is not None
        assert len(settings.app_version) > 0

    def test_environment_has_value(self) -> None:
        assert settings.environment in ("development", "staging", "production", "testing")

    def test_database_url_is_postgresql(self) -> None:
        assert settings.database_url.startswith("postgresql+asyncpg://")

    def test_cors_origins_is_list(self) -> None:
        assert isinstance(settings.backend_cors_origins, list)
        assert len(settings.backend_cors_origins) > 0

    def test_llm_provider_is_set(self) -> None:
        assert settings.llm_provider in ("ollama", "openai", "anthropic", "google")

    def test_llm_model_is_set(self) -> None:
        assert settings.llm_model is not None
        assert len(settings.llm_model) > 0

    def test_llm_base_url_is_set(self) -> None:
        assert settings.llm_base_url.startswith("http")
