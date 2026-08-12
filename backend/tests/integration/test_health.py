"""Integration tests for the health check endpoint.

Uses the mocked DB client from conftest.py — no real database needed.
"""

from __future__ import annotations

import pytest
from httpx import AsyncClient


class TestHealthEndpoint:
    async def test_health_returns_200(self, mock_client: AsyncClient) -> None:
        """Health endpoint must always return HTTP 200."""
        response = await mock_client.get("/api/v1/health")
        assert response.status_code == 200

    async def test_health_response_has_required_fields(self, mock_client: AsyncClient) -> None:
        """Response must contain status, version, environment, and database fields."""
        response = await mock_client.get("/api/v1/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "environment" in data
        assert "database" in data

    async def test_health_status_is_ok(self, mock_client: AsyncClient) -> None:
        """Status field must be 'ok' when the API is running."""
        response = await mock_client.get("/api/v1/health")
        assert response.json()["status"] == "ok"

    async def test_health_database_connected_with_mock(self, mock_client: AsyncClient) -> None:
        """With a mocked session, the database check should report 'connected'."""
        response = await mock_client.get("/api/v1/health")
        assert response.json()["database"] == "connected"

    async def test_health_version_is_string(self, mock_client: AsyncClient) -> None:
        """Version field must be a non-empty string."""
        response = await mock_client.get("/api/v1/health")
        version = response.json()["version"]
        assert isinstance(version, str)
        assert len(version) > 0

    async def test_root_endpoint(self, mock_client: AsyncClient) -> None:
        """Root endpoint must return API name and links."""
        response = await mock_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "docs" in data
