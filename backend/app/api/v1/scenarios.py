"""API Router for Natural Language Scenario Analysis.

Integrates Phase 4A AI Scenario Extraction, Entity Matching, Phase 4B RAG Research Retrieval,
Enterprise Semantic Retrieval (Surprise Record support), and Executive Explanation with
Phase 3 Deterministic Intelligence Engine.
"""

from __future__ import annotations

import logging
from typing import List, Optional
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.providers.factory import get_llm_provider
from app.ai.services.explanation_service import ExecutiveExplanationService
from app.ai.services.extraction_service import ScenarioExtractionService
from app.core.dependencies import get_db
from app.db.models import Organisation
from app.engines.entity_matcher import EntityMatcher
from app.engines.semantic_retriever import EnterpriseSemanticRetriever
from app.rag.retriever import ResearchRetriever
from app.schemas.analysis import TransformationAnalysisInput, TransformationAnalysisResponse
from app.schemas.scenario import (
    EntityMatchDetail,
    InformationTrustCategory,
    NaturalLanguageScenarioRequest,
    NaturalLanguageScenarioResponse,
    TrustItemBreakdown,
)
from app.services.analysis_service import AnalysisService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/analysis/scenarios", tags=["Natural Language Scenarios"])


@router.post(
    "",
    response_model=NaturalLanguageScenarioResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Analyze a natural language transformation scenario",
    description=(
        "Processes free-form executive scenario text using LLM extraction, "
        "hybrid entity matching (exact, fuzzy, pgvector semantic search), "
        "pgvector research evidence retrieval, Phase 3 deterministic scoring, "
        "and evidence-grounded executive briefing synthesis."
    ),
)
async def analyze_natural_language_scenario(
    request: NaturalLanguageScenarioRequest,
    db: AsyncSession = Depends(get_db),
) -> NaturalLanguageScenarioResponse:
    """Natural Language Scenario analysis endpoint."""
    # 1. Verify Organisation exists
    org_stmt = select(Organisation).where(Organisation.id == request.organisation_id)
    org_res = await db.execute(org_stmt)
    org = org_res.scalar_one_or_none()
    if not org:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organisation with ID '{request.organisation_id}' not found.",
        )

    # 2. Instantiate Provider & Services
    provider = get_llm_provider()
    extraction_service = ScenarioExtractionService(provider)
    explanation_service = ExecutiveExplanationService(provider)
    entity_matcher = EntityMatcher(db)
    semantic_retriever = EnterpriseSemanticRetriever(db)
    research_retriever = ResearchRetriever(db)

    # 3. Extract Scenario from Natural Language
    extracted, extraction_failed = await extraction_service.extract_scenario(
        organisation_id=request.organisation_id,
        user_input=request.user_input,
        force_refresh=request.force_refresh,
    )

    # 4. Exact/Fuzzy Entity Matching (Tier 1 & Tier 2)
    matched_entities = await entity_matcher.match_extracted_concepts(
        organisation_id=request.organisation_id,
        extracted=extracted,
    )

    # 5. Hybrid Enterprise Semantic Retrieval (pgvector) — Surprise Record Test Support
    # If exact/fuzzy match found no process ID, perform vector search against enterprise embeddings
    if matched_entities.process_match.entity_id is None:
        semantic_matches = await semantic_retriever.search_semantic_entities(
            organisation_id=request.organisation_id,
            query_text=f"{extracted.title} {extracted.description}",
            entity_type="process",
            top_k=1,
            min_similarity=0.15,
        )
        if semantic_matches:
            emb_obj, sim = semantic_matches[0]
            matched_entities.process_match = EntityMatchDetail(
                entity_type="process",
                entity_id=emb_obj.entity_id,
                entity_name=emb_obj.searchable_text.split(".")[0].replace("Process:", "").strip(),
                match_method="vector_semantic",
                match_confidence=sim,
            )
            matched_entities.matched_entity_count += 1

    # 6. Research Evidence Retrieval (pgvector Document Chunks)
    research_result = await research_retriever.search_research_evidence(
        query_text=f"{extracted.title} {extracted.description}",
        organisation_id=request.organisation_id,
        top_k=5,
    )

    # 7. Build Phase 3 Analysis Input (delegating matched entity IDs)
    analysis_input = TransformationAnalysisInput(
        organisation_id=request.organisation_id,
        title=extracted.title,
        description=extracted.description,
        opportunity_id=matched_entities.opportunity_match.entity_id,
        process_id=matched_entities.process_match.entity_id,
        strategy_id=matched_entities.strategy_match.entity_id,
    )

    # 8. Execute Phase 3 Deterministic Engine (Impact, Dependency, Governance, Scoring)
    # Priority score is 100% authoritative and generated strictly by Phase 3 ScoringEngine
    analysis_service = AnalysisService(db)
    analysis_orm = await analysis_service.analyze_transformation(analysis_input)
    analysis_response = TransformationAnalysisResponse.from_orm_model(analysis_orm)

    # 9. Generate Executive Explanation
    explanation = await explanation_service.generate_explanation(analysis_response.model_dump(mode="json"))

    # 10. Construct Information Trust Model Breakdown
    trust_breakdown = _build_trust_breakdown(
        analysis=analysis_response,
        extracted=extracted,
        matched=matched_entities,
        research_result=research_result,
    )

    citations_list = [c.model_dump(mode="json") for c in research_result.citations]
    conflicts_list = [c.model_dump(mode="json") for c in research_result.conflicts]

    return NaturalLanguageScenarioResponse(
        analysis=analysis_response,
        extracted_scenario=extracted,
        matched_entities=matched_entities,
        executive_explanation=explanation,
        research_citations=citations_list,
        research_conflicts=conflicts_list,
        information_trust_breakdown=trust_breakdown,
        ai_enhancement_failed=extraction_failed,
        research_evidence_available=research_result.evidence_available,
    )


def _build_trust_breakdown(
    analysis: TransformationAnalysisResponse,
    extracted: Any,
    matched: Any,
    research_result: Any,
) -> List[TrustItemBreakdown]:
    """Categorize response data items under the Information Trust Model."""
    affected = analysis.affected_entities

    persisted_items = [
        f"Value Chains ({len(affected.get('value_chains', []))}): " + ", ".join([v["name"] for v in affected.get("value_chains", [])]),
        f"Processes ({len(affected.get('processes', []))}): " + ", ".join([p["name"] for p in affected.get("processes", [])]),
        f"Activities ({len(affected.get('activities', []))}): " + ", ".join([a["name"] for a in affected.get("activities", [])]),
        f"Roles ({len(affected.get('roles', []))}): " + ", ".join([r["name"] for r in affected.get("roles", [])]),
        f"Skills ({len(affected.get('skills', []))}): " + ", ".join([s["name"] for s in affected.get("skills", [])]),
        f"Governance Records: {len(analysis.governance_findings)} active audit records",
        f"Deterministic Priority Score: {analysis.priority_score:.1f}/100 ({analysis.priority_category})",
    ]

    inference_items = [
        f"Extracted Domain: {extracted.business_domain} (Confidence: {extracted.llm_extraction_confidence:.2f})",
        f"Transformation Type: {extracted.transformation_type}",
        f"Candidate Processes: {', '.join(extracted.candidate_process_names) if extracted.candidate_process_names else 'None'}",
        f"Process Entity Match: {matched.process_match.entity_name or 'None'} (Confidence: {matched.process_match.match_confidence:.2f}, Method: {matched.process_match.match_method})",
        f"Opportunity Entity Match: {matched.opportunity_match.entity_name or 'None'} (Confidence: {matched.opportunity_match.match_confidence:.2f}, Method: {matched.opportunity_match.match_method})",
    ]

    if research_result.evidence_available:
        research_items = [
            f"Configured Evidence Threshold: {research_result.configured_threshold:.2f}",
            f"Retrieved Candidate Chunks ({len(research_result.candidate_chunks)}): " + "; ".join([f"'{c.title}' (Sim: {c.similarity_score:.2f}, Threshold Met: {c.meets_supporting_threshold})" for c in research_result.candidate_chunks[:3]]),
            f"Supporting Evidence Citations ({len(research_result.citations)}): " + "; ".join([f"[{c.evidence_label}: {c.publisher}] '{c.title}' (Sim: {c.similarity_score:.2f}, URL: {c.url})" for c in research_result.citations]),
            f"Vector Query Latency: {research_result.query_vector_latency_ms:.2f} ms",
        ]
        if research_result.conflicts:
            research_items.append(f"Research Conflicts Detected ({len(research_result.conflicts)}): " + "; ".join([c.description for c in research_result.conflicts]))
    else:
        research_items = [
            f"Configured Evidence Threshold: {research_result.configured_threshold:.2f}",
            f"No supporting external research evidence retrieved meeting configured similarity threshold ({research_result.configured_threshold:.2f}).",
            f"Vector Query Latency: {research_result.query_vector_latency_ms:.2f} ms",
        ]

    return [
        TrustItemBreakdown(
            category=InformationTrustCategory.PERSISTED_FACT,
            source_description="PostgreSQL enterprise domain model, relationships, governance, and Phase 3 scoring engine.",
            items=persisted_items,
        ),
        TrustItemBreakdown(
            category=InformationTrustCategory.AI_INFERENCE,
            source_description="LLM natural language extraction and EntityMatcher fuzzy/semantic similarity.",
            items=inference_items,
        ),
        TrustItemBreakdown(
            category=InformationTrustCategory.RESEARCH_EVIDENCE,
            source_description="Verified research evidence chunks retrieved from pgvector vector index.",
            items=research_items,
        ),
    ]
