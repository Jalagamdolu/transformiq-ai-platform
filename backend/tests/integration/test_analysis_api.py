"""Integration tests for Phase 3 Transformation Intelligence Analysis API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_analyze_existing_opportunity(client: AsyncClient):
    """Test POST /api/v1/analysis/opportunities/{opportunity_id} on NovaMart data."""
    # 1. Fetch NovaMart AI Opportunities
    opps_resp = await client.get("/api/v1/opportunities")
    assert opps_resp.status_code == 200
    opps = opps_resp.json()["items"]
    assert len(opps) > 0

    # Pick Demand Forecasting opportunity
    target_opp = next((o for o in opps if "Demand Forecasting" in o["name"]), opps[0])
    opp_id = target_opp["id"]

    # 2. Run analysis on Opportunity
    analysis_resp = await client.post(f"/api/v1/analysis/opportunities/{opp_id}")
    assert analysis_resp.status_code == 201
    data = analysis_resp.json()

    assert data["opportunity_id"] == opp_id
    assert "priority_score" in data
    assert data["priority_category"] in ("HIGH", "MEDIUM", "LOW")
    assert "factor_scores" in data
    assert "affected_entities" in data
    assert "governance_findings" in data
    assert "dependency_findings" in data

    # Verify non-empty roles and skills in relationship propagation
    affected = data["affected_entities"]
    assert len(affected["roles"]) > 0, "affected_entities.roles must be non-empty after Phase 3.1 fix!"
    assert len(affected["skills"]) > 0, "affected_entities.skills must be non-empty after Phase 3.1 fix!"

    # Verify specific roles and skills traversed
    role_names = [r["name"] for r in affected["roles"]]
    skill_names = [s["name"] for s in affected["skills"]]
    assert "Demand Planner" in role_names
    assert "Demand Forecasting" in skill_names

    # 3. Retrieve analysis by ID via GET /api/v1/analysis/transformations/{id}
    analysis_id = data["id"]
    get_resp = await client.get(f"/api/v1/analysis/transformations/{analysis_id}")
    assert get_resp.status_code == 200
    get_data = get_resp.json()
    assert get_data["id"] == analysis_id
    assert get_data["priority_score"] == data["priority_score"]


@pytest.mark.asyncio
async def test_analyze_existing_process(client: AsyncClient):
    """Test POST /api/v1/analysis/processes/{process_id} on NovaMart Demand Forecasting process."""
    # 1. Fetch NovaMart processes
    proc_resp = await client.get("/api/v1/processes")
    assert proc_resp.status_code == 200
    procs = proc_resp.json()["items"]
    assert len(procs) > 0

    target_proc = next((p for p in procs if "Demand Forecasting" in p["name"]), procs[0])
    proc_id = target_proc["id"]

    # 2. Run analysis on Process
    analysis_resp = await client.post(f"/api/v1/analysis/processes/{proc_id}")
    assert analysis_resp.status_code == 201
    data = analysis_resp.json()

    assert data["process_id"] == proc_id
    assert data["priority_score"] > 0
    assert len(data["affected_entities"]["activities"]) > 0
    assert len(data["affected_entities"]["roles"]) > 0, "Process analysis must propagate to roles!"
    assert len(data["affected_entities"]["skills"]) > 0, "Process analysis must propagate to skills!"


@pytest.mark.asyncio
async def test_analyze_custom_scenario(client: AsyncClient):
    """Test POST /api/v1/analysis/transformations for custom scenario."""
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    payload = {
        "organisation_id": org_id,
        "title": "Custom Integration Test Transformation Scenario",
        "description": "Evaluating automated checkout and smart logistics",
    }
    resp = await client.post("/api/v1/analysis/transformations", json=payload)
    assert resp.status_code == 201
    data = resp.json()
    assert data["organisation_id"] == org_id
    assert data["title"] == payload["title"]


@pytest.mark.asyncio
async def test_list_analyses_for_organisation(client: AsyncClient):
    """Test GET /api/v1/analysis/transformations?organisation_id=..."""
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]

    resp = await client.get(f"/api/v1/analysis/transformations?organisation_id={org_id}")
    assert resp.status_code == 200
    data = resp.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_analyze_invalid_opportunity_returns_404(client: AsyncClient):
    bad_id = "00000000-0000-0000-0000-000000000000"
    resp = await client.post(f"/api/v1/analysis/opportunities/{bad_id}")
    assert resp.status_code == 404
