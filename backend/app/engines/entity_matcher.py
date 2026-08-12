"""Enterprise Entity Matcher Engine.

Matches extracted natural language concepts against PostgreSQL domain entities
using Tier 1 (Normalized Exact Match) and Tier 2 (Token Similarity Match).
"""

from __future__ import annotations

import re
import uuid
from typing import List, Optional, Set, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AIOpportunity, Process, Strategy, ValueChain
from app.schemas.scenario import (
    EntityMatchDetail,
    ExtractedScenarioSpec,
    MatchedEntitiesResult,
)


class EntityMatcher:
    """Matches natural language terms against database entities in PostgreSQL."""

    MATCH_THRESHOLD = 0.65  # Minimum confidence threshold required to accept a match

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def match_extracted_concepts(
        self,
        organisation_id: uuid.UUID,
        extracted: ExtractedScenarioSpec,
    ) -> MatchedEntitiesResult:
        """Run 2-Tier matching for extracted scenario terms against database entities.

        Returns:
            MatchedEntitiesResult containing details for process, opportunity, value chain, and strategy matches.
        """
        # 1. Match Process
        proc_match = await self._match_process(organisation_id, extracted)

        # 2. Match Opportunity
        opp_match = await self._match_opportunity(organisation_id, extracted)

        # 3. Match ValueChain
        vc_match = await self._match_value_chain(organisation_id, extracted)

        # 4. Match Strategy
        strat_match = await self._match_strategy(organisation_id, extracted)

        matched_count = sum(
            1 for m in [proc_match, opp_match, vc_match, strat_match] if m.entity_id is not None
        )

        return MatchedEntitiesResult(
            process_match=proc_match,
            opportunity_match=opp_match,
            value_chain_match=vc_match,
            strategy_match=strat_match,
            matched_entity_count=matched_count,
        )

    async def _match_process(
        self, organisation_id: uuid.UUID, extracted: ExtractedScenarioSpec
    ) -> EntityMatchDetail:
        stmt = select(Process).where(Process.organisation_id == organisation_id)
        res = await self.session.execute(stmt)
        processes = res.scalars().all()

        query_terms = [extracted.title, extracted.description] + extracted.candidate_process_names
        return self._find_best_match(
            entities=processes,
            query_terms=query_terms,
            entity_type="process",
        )

    async def _match_opportunity(
        self, organisation_id: uuid.UUID, extracted: ExtractedScenarioSpec
    ) -> EntityMatchDetail:
        stmt = select(AIOpportunity).where(AIOpportunity.organisation_id == organisation_id)
        res = await self.session.execute(stmt)
        opportunities = res.scalars().all()

        query_terms = [extracted.title, extracted.description]
        return self._find_best_match(
            entities=opportunities,
            query_terms=query_terms,
            entity_type="opportunity",
        )

    async def _match_value_chain(
        self, organisation_id: uuid.UUID, extracted: ExtractedScenarioSpec
    ) -> EntityMatchDetail:
        stmt = select(ValueChain).where(ValueChain.organisation_id == organisation_id)
        res = await self.session.execute(stmt)
        value_chains = res.scalars().all()

        query_terms = [extracted.title, extracted.description] + extracted.candidate_value_chains
        return self._find_best_match(
            entities=value_chains,
            query_terms=query_terms,
            entity_type="value_chain",
        )

    async def _match_strategy(
        self, organisation_id: uuid.UUID, extracted: ExtractedScenarioSpec
    ) -> EntityMatchDetail:
        stmt = select(Strategy).where(Strategy.organisation_id == organisation_id)
        res = await self.session.execute(stmt)
        strategies = res.scalars().all()

        query_terms = [extracted.title, extracted.description]
        return self._find_best_match(
            entities=strategies,
            query_terms=query_terms,
            entity_type="strategy",
        )

    def _find_best_match(
        self,
        entities: List[Any],
        query_terms: List[str],
        entity_type: str,
    ) -> EntityMatchDetail:
        best_entity = None
        best_confidence = 0.0
        best_method = "none"

        for term in query_terms:
            if not term:
                continue

            norm_term = self._normalize(term)

            for entity in entities:
                norm_name = self._normalize(entity.name)

                # Tier 1: Exact Normalized Match
                if norm_term == norm_name or norm_name in norm_term or norm_term in norm_name:
                    confidence = 1.0 if norm_term == norm_name else 0.85
                    method = "exact" if norm_term == norm_name else "token_fuzzy"

                    if confidence > best_confidence:
                        best_entity = entity
                        best_confidence = confidence
                        best_method = method
                    continue

                # Tier 2: Token Similarity / Jaccard Overlap
                jaccard_score = self._compute_jaccard_similarity(term, entity.name)
                if jaccard_score >= self.MATCH_THRESHOLD and jaccard_score > best_confidence:
                    best_entity = entity
                    best_confidence = round(jaccard_score, 2)
                    best_method = "token_fuzzy"

        # Apply minimum confidence threshold (Rule: do not force low confidence match)
        if best_entity and best_confidence >= self.MATCH_THRESHOLD:
            return EntityMatchDetail(
                entity_type=entity_type,
                entity_id=best_entity.id,
                entity_name=best_entity.name,
                match_method=best_method,
                match_confidence=best_confidence,
            )

        return EntityMatchDetail(
            entity_type=entity_type,
            entity_id=None,
            entity_name=None,
            match_method="none",
            match_confidence=0.0,
        )

    @staticmethod
    def _normalize(text: str) -> str:
        text = text.lower()
        return re.sub(r"[^\w\s]", "", text).strip()

    @classmethod
    def _compute_jaccard_similarity(cls, str1: str, str2: str) -> float:
        tokens1: Set[str] = set(cls._normalize(str1).split())
        tokens2: Set[str] = set(cls._normalize(str2).split())
        if not tokens1 or not tokens2:
            return 0.0
        intersection = tokens1.intersection(tokens2)
        union = tokens1.union(tokens2)
        return len(intersection) / len(union)
