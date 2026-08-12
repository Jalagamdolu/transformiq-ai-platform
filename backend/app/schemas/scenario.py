"""Pydantic schemas for Phase 4A/4B AI Scenario extraction, Entity Matching, Executive Explanation, RAG, and Trust Model.

Enforces strict input/output validation across the AI layer and API endpoints.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.analysis import TransformationAnalysisResponse


class InformationTrustCategory(str, Enum):
    """Trust categorization for analysis information sources."""

    PERSISTED_FACT = "persisted_fact"
    AI_INFERENCE = "ai_inference"
    RESEARCH_EVIDENCE = "research_evidence"


class ExtractedScenarioSpec(BaseModel):
    """Structured scenario parameters extracted from natural language by LLM."""

    model_config = ConfigDict(extra="forbid")

    title: str = Field(
        ...,
        min_length=3,
        description="Short title summarizing the transformation initiative.",
    )
    description: str = Field(
        ...,
        min_length=10,
        description="Comprehensive summary of proposed change.",
    )
    business_domain: str = Field(
        ...,
        description="Target business domain (e.g. Supply Chain, Customer Experience, Store Operations).",
    )
    transformation_type: str = Field(
        ...,
        description="Type of transformation (automation, optimization, augmentation, generation).",
    )
    candidate_process_names: List[str] = Field(
        default_factory=list,
        description="Names of candidate business processes mentioned or implied.",
    )
    candidate_value_chains: List[str] = Field(
        default_factory=list,
        description="Names of candidate value chains mentioned or implied.",
    )
    candidate_ai_opportunity_category: str = Field(
        default="automation",
        description="Estimated AI category: automation, analytics, augmentation, generation, optimization.",
    )
    candidate_roles: List[str] = Field(
        default_factory=list,
        description="Target job roles impacted.",
    )
    candidate_skills: List[str] = Field(
        default_factory=list,
        description="Target skills impacted or required.",
    )
    llm_extraction_confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Model self-reported extraction confidence (0.0 to 1.0). Separate from match confidence.",
    )
    assumptions: List[str] = Field(
        default_factory=list,
        description="Key assumptions made during natural language extraction.",
    )


class EntityMatchDetail(BaseModel):
    """Details of an individual entity match attempt."""

    model_config = ConfigDict(extra="forbid")

    entity_type: str = Field(..., description="Entity type: process, opportunity, value_chain, strategy.")
    entity_id: Optional[UUID] = Field(default=None, description="Matched database entity UUID if found.")
    entity_name: Optional[str] = Field(default=None, description="Matched database entity name.")
    match_method: str = Field(default="none", description="Match tier: exact, token_fuzzy, vector_semantic, none.")
    match_confidence: float = Field(default=0.0, ge=0.0, le=1.0, description="Match confidence score (0.0 to 1.0).")


class MatchedEntitiesResult(BaseModel):
    """Aggregate result of entity matching across database domains."""

    model_config = ConfigDict(extra="forbid")

    process_match: EntityMatchDetail = Field(default_factory=lambda: EntityMatchDetail(entity_type="process"))
    opportunity_match: EntityMatchDetail = Field(default_factory=lambda: EntityMatchDetail(entity_type="opportunity"))
    value_chain_match: EntityMatchDetail = Field(default_factory=lambda: EntityMatchDetail(entity_type="value_chain"))
    strategy_match: EntityMatchDetail = Field(default_factory=lambda: EntityMatchDetail(entity_type="strategy"))
    matched_entity_count: int = Field(default=0, description="Count of successfully matched database entities.")


class ExecutiveExplanation(BaseModel):
    """Structured executive briefing synthesized from deterministic analysis."""

    model_config = ConfigDict(extra="forbid")

    executive_summary: str = Field(..., description="High-level C-suite summary of priority score and strategic context.")
    strategic_rationale: str = Field(..., description="Detailed strategic alignment and business value breakdown.")
    key_impacted_areas: List[str] = Field(..., description="Key enterprise processes, roles, and skills impacted.")
    risk_and_governance_advice: List[str] = Field(..., description="Governance risks, compliance requirements, and mitigation advice.")
    recommended_next_steps: List[str] = Field(..., description="Actionable recommendations for initiative implementation.")


class NaturalLanguageScenarioRequest(BaseModel):
    """Input payload for POST /api/v1/analysis/scenarios."""

    model_config = ConfigDict(extra="forbid")

    organisation_id: UUID = Field(..., description="UUID of the organisation.")
    user_input: str = Field(
        ...,
        min_length=10,
        max_length=2000,
        description="Natural language scenario description from user.",
    )
    force_refresh: bool = Field(
        default=False,
        description="If True, bypasses extraction cache and forces fresh LLM call.",
    )


class TrustItemBreakdown(BaseModel):
    """Categorized summary of data elements by trust level."""

    model_config = ConfigDict(extra="forbid")

    category: InformationTrustCategory
    source_description: str
    items: List[str]


class NaturalLanguageScenarioResponse(BaseModel):
    """Complete response object returned by natural language scenario API."""

    model_config = ConfigDict(extra="forbid")

    # Embedded Phase 3 Deterministic Analysis Result
    analysis: TransformationAnalysisResponse = Field(..., description="Phase 3 deterministic analysis output.")
    
    # Phase 4A/4B AI & RAG Enrichment Fields
    extracted_scenario: ExtractedScenarioSpec = Field(..., description="Structured scenario parameters extracted by LLM.")
    matched_entities: MatchedEntitiesResult = Field(..., description="Database entity matching results.")
    executive_explanation: ExecutiveExplanation = Field(..., description="Synthesized executive briefing.")
    research_citations: List[Dict[str, Any]] = Field(default_factory=list, description="Verified research citations with dynamic similarity scores.")
    research_conflicts: List[Dict[str, Any]] = Field(default_factory=list, description="Material research evidence conflicts surfaced.")
    information_trust_breakdown: List[TrustItemBreakdown] = Field(..., description="Information categorization by trust model.")
    ai_enhancement_failed: bool = Field(default=False, description="True if LLM failed and fallback logic was executed.")
    research_evidence_available: bool = Field(default=False, description="True if verified external research evidence was retrieved.")
