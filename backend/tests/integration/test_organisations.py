"""Integration tests for Organisation API endpoints and Repository operations."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_organisation_crud_flow(client: AsyncClient):
    """Test full Organisation API CRUD flow."""
    unique_name = f"Test Enterprise Retail Corp {uuid.uuid4().hex[:8]}"
    new_org_payload = {
        "name": unique_name,
        "industry": "Supermarkets",
        "description": "Integration test organisation",
        "is_active": True,
    }
    # 1. Create a new Organisation via POST
    create_resp = await client.post("/api/v1/organisations", json=new_org_payload)
    assert create_resp.status_code == 201
    org_data = create_resp.json()
    assert org_data["name"] == new_org_payload["name"]
    assert "id" in org_data
    org_id = org_data["id"]

    # 2. Duplicate name creation attempt (409 Conflict)
    dup_resp = await client.post("/api/v1/organisations", json=new_org_payload)
    assert dup_resp.status_code == 409

    # 3. Retrieve by ID (200 OK)
    get_resp = await client.get(f"/api/v1/organisations/{org_id}")
    assert get_resp.status_code == 200
    assert get_resp.json()["id"] == org_id

    # 4. List all organisations (should contain NovaMart + test org)
    list_resp = await client.get("/api/v1/organisations")
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 2
