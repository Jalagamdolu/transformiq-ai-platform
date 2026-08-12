"""Integration test for Phase 4B / Phase 5 Surprise Record Scenarios and Provenance Verification."""

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from app.db.models import Organisation, Process
from app.db.session import AsyncSessionLocal
from app.engines.semantic_retriever import EnterpriseSemanticRetriever


@pytest.mark.asyncio
async def test_surprise_record_warehouse_slotting_optimization(client: AsyncClient):
    """Surprise Record Test: Unseeded warehouse slotting scenario."""
    # 1. Fetch NovaMart org ID
    orgs_resp = await client.get("/api/v1/organisations")
    assert orgs_resp.status_code == 200
    items = orgs_resp.json()["items"]
    org = next((o for o in items if o["name"] == "NovaMart"), items[0])
    org_id = org["id"]

    # 2. Submit Surprise Record Scenario
    user_input = "AI-powered warehouse slotting optimisation"
    payload = {
        "organisation_id": org_id,
        "user_input": user_input,
        "force_refresh": True,
    }

    resp = await client.post("/api/v1/analysis/scenarios", json=payload)
    assert resp.status_code == 201, f"Failed with {resp.status_code}: {resp.text}"
    data = resp.json()

    # 3. Verify Response Top-Level Structure
    assert "analysis" in data
    assert "extracted_scenario" in data
    assert "matched_entities" in data
    assert "executive_explanation" in data
    assert "research_citations" in data
    assert "information_trust_breakdown" in data

    # 4. Verify Surprise Record Processing
    extracted = data["extracted_scenario"]
    assert "slotting" in extracted["title"].lower() or "warehouse" in extracted["title"].lower()

    # 5. Verify Enterprise Semantic Retrieval Match (pgvector)
    matched = data["matched_entities"]
    assert matched["matched_entity_count"] >= 1
    assert matched["process_match"]["match_confidence"] >= 0.15
    assert matched["process_match"]["entity_name"] in (
        "Store Inventory Management",
        "Supplier Order Fulfillment",
        "Demand Forecasting",
    )

    # 6. Verify Phase 3 Deterministic Scoring Authority
    analysis = data["analysis"]
    assert analysis["priority_score"] > 0.0
    assert analysis["priority_category"] in ("HIGH", "MEDIUM", "LOW")
    assert len(analysis["affected_entities"]["processes"]) >= 1

    # 7. Verify Information Trust Model Categorization
    trust = data["information_trust_breakdown"]
    categories = [t["category"] for t in trust]
    assert "persisted_fact" in categories
    assert "ai_inference" in categories
    assert "research_evidence" in categories


@pytest.mark.asyncio
async def test_surprise_record_workforce_scheduling(client: AsyncClient):
    """Regression Test for Scenario 3: AI-assisted workforce scheduling.

    Verifies that 'Workforce Scheduling' process in NovaMart enterprise DB
    is dynamically matched via exact matching without hard-coding.
    """
    orgs_resp = await client.get("/api/v1/organisations")
    items = orgs_resp.json()["items"]
    org = next((o for o in items if o["name"] == "NovaMart"), items[0])
    org_id = org["id"]

    payload = {
        "organisation_id": org_id,
        "user_input": "AI-assisted workforce scheduling",
        "force_refresh": True,
    }

    resp = await client.post("/api/v1/analysis/scenarios", json=payload)
    assert resp.status_code == 201
    data = resp.json()

    matched = data["matched_entities"]
    assert matched["process_match"]["entity_name"] == "Workforce Scheduling"
    assert matched["process_match"]["match_method"] == "exact"
    assert matched["process_match"]["match_confidence"] == 1.0
    assert data["analysis"]["priority_score"] > 0.0


@pytest.mark.asyncio
async def test_surprise_record_provenance_dynamic_vector_search():
    """Provenance Verification Test.

    Directly tests EnterpriseSemanticRetriever to prove that 'warehouse slotting optimisation'
    dynamically retrieves 'Demand Forecasting' or 'Store Inventory Management' via pgvector vector similarity,
    and would fail if any hardcoded mapping were relied upon.
    """
    async with AsyncSessionLocal() as session:
        # 1. Fetch NovaMart org
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()
        assert org is not None

        # 2. Instantiate EnterpriseSemanticRetriever
        retriever = EnterpriseSemanticRetriever(session)

        # 3. Execute vector search directly with unseeded text (no MockLLM involved)
        unseeded_query = "AI-powered warehouse slotting layout optimization"
        matches = await retriever.search_semantic_entities(
            organisation_id=org.id,
            query_text=unseeded_query,
            entity_type="process",
            top_k=1,
            min_similarity=0.15,
        )

        assert len(matches) == 1, "pgvector search should dynamically retrieve an enterprise process."
        emb_obj, sim = matches[0]

        # Verify the dynamically matched process ID
        proc_stmt = select(Process).where(Process.id == emb_obj.entity_id)
        proc_res = await session.execute(proc_stmt)
        proc = proc_res.scalar_one()

        assert proc.name in ("Store Inventory Management", "Demand Forecasting")
        assert sim >= 0.15
