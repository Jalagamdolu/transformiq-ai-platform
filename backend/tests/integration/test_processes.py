"""Integration tests for Strategy, Process, Activity, Opportunity, Governance, and Initiative APIs."""

import uuid
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_domain_collection_endpoints(client: AsyncClient):
    """Test all domain collection endpoints return 200 with pagination structure."""
    endpoints = [
        "/api/v1/strategies",
        "/api/v1/value-chains",
        "/api/v1/processes",
        "/api/v1/activities",
        "/api/v1/opportunities",
        "/api/v1/roles",
        "/api/v1/skills",
        "/api/v1/initiatives",
    ]
    for ep in endpoints:
        resp = await client.get(ep)
        assert resp.status_code == 200, f"Endpoint {ep} failed with {resp.status_code}"
        data = resp.json()
        assert "items" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data


@pytest.mark.asyncio
async def test_strategy_and_process_creation(client: AsyncClient):
    """Test creation and retrieval of Strategy, ValueChain, Process, and Activity."""
    # 1. Fetch NovaMart org ID
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]
    suffix = uuid.uuid4().hex[:8]

    # 2. Create Strategy
    strat_payload = {
        "organisation_id": org_id,
        "name": f"Integration Test Strategy {suffix}",
        "description": "Test strategy",
        "status": "active",
        "time_horizon": "2026-2027",
    }
    strat_resp = await client.post("/api/v1/strategies", json=strat_payload)
    assert strat_resp.status_code == 201
    strat_id = strat_resp.json()["id"]

    # Fetch strategy by ID
    get_strat = await client.get(f"/api/v1/strategies/{strat_id}")
    assert get_strat.status_code == 200

    # 3. Create ValueChain
    vc_payload = {
        "organisation_id": org_id,
        "strategy_id": strat_id,
        "name": f"Integration Test Value Chain {suffix}",
        "description": "Test VC",
    }
    vc_resp = await client.post("/api/v1/value-chains", json=vc_payload)
    assert vc_resp.status_code == 201
    vc_id = vc_resp.json()["id"]

    # 4. Create Process
    proc_payload = {
        "organisation_id": org_id,
        "value_chain_id": vc_id,
        "name": f"Integration Test Process {suffix}",
        "description": "Test process",
        "process_type": "operational",
        "status": "active",
    }
    proc_resp = await client.post("/api/v1/processes", json=proc_payload)
    assert proc_resp.status_code == 201
    proc_id = proc_resp.json()["id"]

    # 5. Create Activity
    act_payload = {
        "process_id": proc_id,
        "name": f"Integration Test Activity {suffix}",
        "description": "Test activity step",
        "activity_type": "automated",
        "sequence_order": 1,
    }
    act_resp = await client.post("/api/v1/activities", json=act_payload)
    assert act_resp.status_code == 201
    act_id = act_resp.json()["id"]

    # Get activity by ID
    get_act = await client.get(f"/api/v1/activities/{act_id}")
    assert get_act.status_code == 200


@pytest.mark.asyncio
async def test_opportunity_and_governance_flow(client: AsyncClient):
    """Test AI Opportunity and Governance creation flow."""
    orgs_resp = await client.get("/api/v1/organisations")
    org_id = orgs_resp.json()["items"][0]["id"]
    suffix = uuid.uuid4().hex[:8]

    # Create AI Opportunity
    opp_payload = {
        "organisation_id": org_id,
        "name": f"Integration Test AI Opportunity {suffix}",
        "description": "Testing AI opportunity API",
        "category": "automation",
        "status": "identified",
        "ai_technology": "LLM Test",
    }
    opp_resp = await client.post("/api/v1/opportunities", json=opp_payload)
    assert opp_resp.status_code == 201
    opp_id = opp_resp.json()["id"]

    # Get opportunity by ID
    get_opp = await client.get(f"/api/v1/opportunities/{opp_id}")
    assert get_opp.status_code == 200

    # Add Governance record
    gov_payload = {
        "ai_opportunity_id": opp_id,
        "category": "privacy",
        "risk_level": "medium",
        "description": "Governance risk evaluation",
        "notes": "Audited in integration test",
    }
    gov_resp = await client.post(f"/api/v1/opportunities/{opp_id}/governance", json=gov_payload)
    assert gov_resp.status_code == 201

    # List Governance records for opportunity
    list_gov = await client.get(f"/api/v1/opportunities/{opp_id}/governance")
    assert list_gov.status_code == 200
    assert list_gov.json()["total"] >= 1
