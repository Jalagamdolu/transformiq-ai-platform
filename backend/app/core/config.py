"""Application configuration using Pydantic Settings.

All settings are read from environment variables or a .env file.
Defaults are provided so tests run without any .env file present.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration for the TransformIQ backend.

    Priority (highest → lowest):
      1. Actual environment variables
      2. Values in the .env file
      3. Field defaults defined here
    """

    model_config = SettingsConfigDict(
        # Look for .env in the backend/ directory (where uvicorn is started from)
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        # Ignore extra env vars that are not defined here
        extra="ignore",
    )

    # ── Application ──────────────────────────────────────────────────────────
    app_name: str = "TransformIQ API"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = False

    # ── Database ─────────────────────────────────────────────────────────────
    database_url: str = (
        "postgresql+asyncpg://transformiq:transformiq_dev@localhost:5432/transformiq"
    )

    # ── CORS ─────────────────────────────────────────────────────────────────
    # Stored as a JSON string in .env: ["http://localhost:5173"]
    backend_cors_origins: List[str] = ["http://localhost:5173"]

    # ── LLM Configuration ───────────────────────────────────────────────────
    llm_provider: str = "ollama"
    llm_model: str = "llama3.1"
    llm_base_url: str = "http://localhost:11434"
    llm_api_key: str = ""  # Required only for cloud providers

    # ── RAG Research Configuration (Phase 4B) ────────────────────────────────
    rag_min_similarity_threshold: float = 0.30


# Single shared instance — import this everywhere.
settings = Settings()
