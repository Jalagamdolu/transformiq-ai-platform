"""Integration tests for Phase 4A Natural Language Scenario API."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_natural_language_supplier_risk_scenario(client: AsyncClient):
    """End-to-End test for supplier risk assessment natural language scenario."""
    # 1. Fetch NovaMart org ID
    orgs_resp = await client.get("/api/v1/organisations")
    assert orgs_resp.status_code == 200
    items = orgs_resp.json()["items"]
    org = next((o for o in items if o["name"] == "NovaMart"), items[0])
    org_id = org["id"]

    # 2. Submit Natural Language Scenario Request
    user_scenario = "We want to introduce AI-powered supplier risk assessment across our retail supply chain."
    payload = {
        "organisation_id": org_id,
        "user_input": user_scenario,
        "force_refresh": True,
    }

    resp = await client.post("/api/v1/analysis/scenarios", json=payload)
    assert resp.status_code == 201, f"Endpoint failed with {resp.status_code}: {resp.text}"
    data = resp.json()

    # 3. Verify Response Top-Level Structure
    assert "analysis" in data
    assert "extracted_scenario" in data
    assert "matched_entities" in data
    assert "executive_explanation" in data
    assert "information_trust_breakdown" in data
    assert data["ai_enhancement_failed"] is False

    # 4. Verify AI Extraction
    extracted = data["extracted_scenario"]
    assert "supplier risk" in extracted["title"].lower() or "supplier" in extracted["title"].lower()
    assert extracted["llm_extraction_confidence"] > 0.0

    # 5. Verify Entity Matching
    matched = data["matched_entities"]
    assert matched["matched_entity_count"] >= 1
    assert matched["process_match"]["match_confidence"] >= 0.65

    # 6. Verify Phase 3 Deterministic Scoring Integration
    analysis = data["analysis"]
    assert analysis["priority_score"] > 0.0
    assert analysis["priority_category"] in ("HIGH", "MEDIUM", "LOW")
    assert len(analysis["affected_entities"]["processes"]) > 0

    # 7. Verify Executive Explanation Synthesis
    explanation = data["executive_explanation"]
    assert len(explanation["executive_summary"]) > 10
    assert len(explanation["recommended_next_steps"]) >= 1

    # 8. Verify Information Trust Model Breakdown
    trust = data["information_trust_breakdown"]
    assert len(trust) == 3
    categories = [t["category"] for t in trust]
    assert "persisted_fact" in categories
    assert "ai_inference" in categories
    assert "research_evidence" in categories


@pytest.mark.asyncio
async def test_natural_language_scenario_invalid_org_returns_404(client: AsyncClient):
    bad_id = "00000000-0000-0000-0000-000000000000"
    payload = {
        "organisation_id": bad_id,
        "user_input": "Automate inventory reordering using machine learning.",
    }
    resp = await client.post("/api/v1/analysis/scenarios", json=payload)
    assert resp.status_code == 404
