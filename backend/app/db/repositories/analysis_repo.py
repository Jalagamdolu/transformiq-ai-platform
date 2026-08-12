"""TransformationAnalysis Repository."""

from __future__ import annotations

import uuid
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import select

from app.db.models.transformation_analysis import TransformationAnalysis
from app.db.repositories.base import BaseRepository


class AnalysisRepository(BaseRepository[TransformationAnalysis]):
    model_class = TransformationAnalysis

    async def get_by_organisation(
        self,
        organisation_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[TransformationAnalysis], int]:
        return await self.get_all(
            skip=skip, limit=limit, organisation_id=organisation_id
        )

    async def create_analysis(
        self,
        organisation_id: uuid.UUID,
        title: str,
        description: Optional[str],
        opportunity_id: Optional[uuid.UUID],
        process_id: Optional[uuid.UUID],
        strategy_id: Optional[uuid.UUID],
        priority_score: float,
        priority_category: str,
        factor_scores: Dict[str, Any],
        reason_codes: Dict[str, Any],
        affected_entities: Dict[str, Any],
        governance_findings: Dict[str, Any],
        dependency_findings: Dict[str, Any],
        status: str = "completed",
        engine_version: str = "1.0.0",
    ) -> TransformationAnalysis:
        obj = TransformationAnalysis(
            organisation_id=organisation_id,
            title=title,
            description=description,
            opportunity_id=opportunity_id,
            process_id=process_id,
            strategy_id=strategy_id,
            priority_score=priority_score,
            priority_category=priority_category,
            factor_scores=factor_scores,
            reason_codes=reason_codes,
            affected_entities=affected_entities,
            governance_findings=governance_findings,
            dependency_findings=dependency_findings,
            status=status,
            engine_version=engine_version,
        )
        return await self.create(obj)
