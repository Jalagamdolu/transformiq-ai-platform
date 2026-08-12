"""Transformation Analysis Service.

Orchestrates context discovery, relationship impact traversal, dependency analysis,
deterministic priority scoring, and database persistence.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.organisation import Organisation
from app.db.models.transformation_analysis import TransformationAnalysis
from app.db.repositories.analysis_repo import AnalysisRepository
from app.engines.dependency_engine import DependencyEngine
from app.engines.impact_engine import ImpactEngine
from app.engines.scoring_engine import ScoringEngine
from app.schemas.analysis import TransformationAnalysisInput


class AnalysisService:
    """Service orchestrating end-to-end transformation intelligence analysis."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.impact_engine = ImpactEngine(session)
        self.dependency_engine = DependencyEngine(session)
        self.scoring_engine = ScoringEngine()
        self.analysis_repo = AnalysisRepository(session)

    async def analyze_transformation(
        self, input_data: TransformationAnalysisInput
    ) -> TransformationAnalysis:
        """Run the complete transformation intelligence pipeline and persist the result."""

        # 0. Verify organisation exists
        org_stmt = select(Organisation).where(Organisation.id == input_data.organisation_id)
        org_res = await self.session.execute(org_stmt)
        org = org_res.scalar_one_or_none()
        if not org:
            raise ValueError(f"Organisation {input_data.organisation_id} not found")

        # 1. Discover Context & Impact
        affected_entities, governance_findings, context_meta = (
            await self.impact_engine.discover_impact(
                organisation_id=input_data.organisation_id,
                opportunity_id=input_data.opportunity_id,
                process_id=input_data.process_id,
                strategy_id=input_data.strategy_id,
            )
        )

        # 2. Analyze Dependencies
        entity_type = (
            "opportunity"
            if input_data.opportunity_id
            else "process"
            if input_data.process_id
            else "initiative"
        )
        entity_id = (
            input_data.opportunity_id
            or input_data.process_id
            or input_data.organisation_id
        )

        dependency_findings = await self.dependency_engine.analyze_dependencies(
            organisation_id=input_data.organisation_id,
            entity_type=entity_type,
            entity_id=entity_id,
        )

        # 3. Calculate Deterministic Priority Score & Explanation Factors
        final_score, priority_category, factor_details, reason_codes = (
            self.scoring_engine.evaluate_scenario(
                affected_entities=affected_entities,
                governance_findings=governance_findings,
                dependency_findings=dependency_findings,
                opportunity_status=context_meta.get("primary_opportunity_status"),
                ai_technology=context_meta.get("primary_ai_technology"),
            )
        )

        # 4. Persist Result
        analysis = await self.analysis_repo.create_analysis(
            organisation_id=input_data.organisation_id,
            title=input_data.title,
            description=input_data.description,
            opportunity_id=input_data.opportunity_id,
            process_id=input_data.process_id,
            strategy_id=input_data.strategy_id,
            priority_score=final_score,
            priority_category=priority_category,
            factor_scores=factor_details,
            reason_codes=reason_codes,
            affected_entities=affected_entities,
            governance_findings=governance_findings,
            dependency_findings=dependency_findings,
            status="completed",
            engine_version="1.0.0",
        )

        return analysis

    async def get_analysis_by_id(
        self, analysis_id: uuid.UUID
    ) -> Optional[TransformationAnalysis]:
        return await self.analysis_repo.get_by_id(analysis_id)
