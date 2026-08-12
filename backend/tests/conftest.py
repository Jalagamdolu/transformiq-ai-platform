"""Shared test fixtures and configuration.

Provides:
  - `client`       — AsyncClient connected to the application with DB dependency
  - `mock_client`  — AsyncClient with mocked DB dependency (no DB needed)
"""

from __future__ import annotations

from typing import AsyncGenerator
from unittest.mock import AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings

# Force testing environment for pytest so NullPool is used
settings.environment = "testing"

from app.core.dependencies import get_db
from app.db.session import engine
from app.main import app


# ---------------------------------------------------------------------------
# Real DB client fixture
# ---------------------------------------------------------------------------


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an HTTPX async test client connected to the application."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client


# ---------------------------------------------------------------------------
# Mocked DB client fixture
# ---------------------------------------------------------------------------


async def _mock_get_db() -> AsyncGenerator[AsyncMock, None]:
    """Yield a mocked DB session for unit-style endpoint tests."""
    mock_result = AsyncMock()
    mock_result.scalar_one = AsyncMock(return_value=1)
    mock_result.scalar_one_or_none = AsyncMock(return_value=None)

    mock_scalars = AsyncMock()
    mock_scalars.all = AsyncMock(return_value=[])
    mock_result.scalars = AsyncMock(return_value=mock_scalars)

    session = AsyncMock()
    session.execute = AsyncMock(return_value=mock_result)
    session.close = AsyncMock(return_value=None)
    yield session


@pytest.fixture
async def mock_client() -> AsyncGenerator[AsyncClient, None]:
    """Yield an HTTPX async test client with DB dependency mocked."""
    app.dependency_overrides[get_db] = _mock_get_db
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as test_client:
        yield test_client
    app.dependency_overrides.clear()
