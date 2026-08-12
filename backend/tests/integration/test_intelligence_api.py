"""Integration tests for Phase 5 Executive Transformation Intelligence API endpoints and Organisation Isolation."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_intelligence_priorities_endpoint(client: AsyncClient):
    # 1. Fetch NovaMart org ID
    orgs_resp = await client.get("/api/v1/organisations")
    assert orgs_resp.status_code == 200
    items = orgs_resp.json()["items"]
    org = next((o for o in items if o["name"] == "NovaMart"), items[0])
    org_id = org["id"]

    # 2. Call Priorities Intelligence API
    resp = await client.get(f"/api/v1/intelligence/priorities?organisation_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_opportunities"] == 8
    assert "high_priority_count" in data
    assert "items" in data
    titles = [i["title"] for i in data["items"]]
    assert len(titles) == len(set(titles)), "Priority response must not contain duplicate enterprise entities."


@pytest.mark.asyncio
async def test_intelligence_skills_endpoint(client: AsyncClient):
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    resp = await client.get(f"/api/v1/intelligence/skills?organisation_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_skills_tracked" in data
    assert "skills" in data


@pytest.mark.asyncio
async def test_intelligence_governance_endpoint(client: AsyncClient):
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    resp = await client.get(f"/api/v1/intelligence/governance?organisation_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "total_risk_records" in data
    assert "findings" in data


@pytest.mark.asyncio
async def test_intelligence_dependencies_graph_endpoint(client: AsyncClient):
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    resp = await client.get(f"/api/v1/intelligence/dependencies/graph?organisation_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "nodes" in data
    assert "edges" in data
    assert "has_cycles" in data


@pytest.mark.asyncio
async def test_executive_analyst_chat_endpoint(client: AsyncClient):
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    payload = {
        "organisation_id": org_id,
        "query": "What should we transform first?",
    }
    resp = await client.post("/api/v1/intelligence/analyst", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert data["classified_intent"] == "priority_ranking"
    assert len(data["executive_briefing"]) > 10
    assert len(data["information_trust_breakdown"]) == 3


@pytest.mark.asyncio
async def test_intelligence_api_organisation_isolation_negative_tests(client: AsyncClient):
    """Negative tests proving Organisation A cannot access Organisation B data."""

    # 1. Create Organisation B
    org_b_payload = {
        "name": f"Isolated Org B {uuid.uuid4().hex[:8]}",
        "industry": "Healthcare",
        "description": "Test Org B for isolation verification",
    }
    create_resp = await client.post("/api/v1/organisations", json=org_b_payload)
    assert create_resp.status_code == 201
    org_b_id = create_resp.json()["id"]

    # 2. Fetch NovaMart Org A
    orgs_resp = await client.get("/api/v1/organisations")
    items = orgs_resp.json()["items"]
    org_a = next((o for o in items if o["name"] == "NovaMart"), items[0])
    org_a_id = org_a["id"]

    # 3. Query Org B priorities - should return 0 items (isolated from Org A)
    priorities_b = await client.get(f"/api/v1/intelligence/priorities?organisation_id={org_b_id}")
    assert priorities_b.status_code == 200
    assert priorities_b.json()["total_analyses"] == 0
    assert len(priorities_b.json()["items"]) == 0

    # 4. Query Org B skills - should return 0 skills (isolated from Org A)
    skills_b = await client.get(f"/api/v1/intelligence/skills?organisation_id={org_b_id}")
    assert skills_b.status_code == 200
    assert skills_b.json()["total_skills_tracked"] == 0

    # 5. Query Org B governance - should return 0 risk records (isolated from Org A)
    gov_b = await client.get(f"/api/v1/intelligence/governance?organisation_id={org_b_id}")
    assert gov_b.status_code == 200
    assert gov_b.json()["total_risk_records"] == 0

    # 6. Query non-existent Org ID - returns 404 Not Found across all endpoints
    random_id = str(uuid.uuid4())
    bad_priorities = await client.get(f"/api/v1/intelligence/priorities?organisation_id={random_id}")
    assert bad_priorities.status_code == 404

    bad_analyst = await client.post("/api/v1/intelligence/analyst", json={"organisation_id": random_id, "query": "What should we transform first?"})
    assert bad_analyst.status_code == 404
