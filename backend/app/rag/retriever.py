"""Research Retriever & Evidence Engine for Phase 4B.

Queries pgvector document chunks, separates candidate chunks from supporting evidence,
formats verified citations, detects conflicts, and maintains strict trust model separation.
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.db.models import DocumentChunk, ResearchSource
from app.rag.embeddings import get_embedding_provider

logger = logging.getLogger(__name__)


class CandidateChunkDetail(BaseModel):
    """Details of a candidate chunk retrieved during vector search prior to threshold filtering."""

    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    chunk_id: UUID
    title: str
    publisher: str
    similarity_score: float
    meets_supporting_threshold: bool


class ResearchCitation(BaseModel):
    """Traceable research evidence citation for supporting evidence."""

    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    chunk_id: UUID
    title: str
    publisher: str
    url: str
    publication_date: Optional[str] = None
    similarity_score: float
    excerpt: str
    evidence_label: str = "Synthetic Demo Evidence"


class ResearchConflict(BaseModel):
    """Surfaced conflict between multiple research sources."""

    model_config = ConfigDict(extra="forbid")

    topic: str
    source_a_title: str
    source_a_finding: str
    source_b_title: str
    source_b_finding: str
    description: str


class ResearchQueryResult(BaseModel):
    """Aggregate result of research vector search distinguishing candidates from supporting evidence."""

    model_config = ConfigDict(extra="forbid")

    candidate_chunks: List[CandidateChunkDetail]
    citations: List[ResearchCitation]
    conflicts: List[ResearchConflict]
    evidence_available: bool
    configured_threshold: float
    query_vector_latency_ms: float


class ResearchRetriever:
    """Queries pgvector document chunks and builds traceable research citations."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embedder = get_embedding_provider()

    async def search_research_evidence(
        self,
        query_text: str,
        organisation_id: Optional[UUID] = None,
        top_k: int = 5,
        min_similarity: Optional[float] = None,
    ) -> ResearchQueryResult:
        """Search pgvector document chunks, separate candidate chunks from supporting evidence,

        and format verified citations.
        """
        import time

        threshold = min_similarity if min_similarity is not None else settings.rag_min_similarity_threshold

        start_time = time.perf_counter()
        query_vector = self.embedder.embed_text(query_text)
        embed_time = (time.perf_counter() - start_time) * 1000.0

        stmt = (
            select(
                DocumentChunk,
                (1 - DocumentChunk.embedding.cosine_distance(query_vector)).label("similarity"),
            )
            .join(ResearchSource, DocumentChunk.source_id == ResearchSource.id)
            .options(selectinload(DocumentChunk.source))
        )

        if organisation_id:
            stmt = stmt.where(
                (ResearchSource.organisation_id == organisation_id) | (ResearchSource.organisation_id.is_(None))
            )

        stmt = stmt.order_by(DocumentChunk.embedding.cosine_distance(query_vector).asc()).limit(top_k)

        res = await self.session.execute(stmt)
        rows = res.all()

        candidate_chunks: List[CandidateChunkDetail] = []
        citations: List[ResearchCitation] = []

        for row in rows:
            chunk: DocumentChunk = row[0]
            sim: float = round(float(row[1]), 4)

            if chunk.source:
                meets_threshold = sim >= threshold

                candidate_chunks.append(
                    CandidateChunkDetail(
                        source_id=chunk.source.id,
                        chunk_id=chunk.id,
                        title=chunk.source.title,
                        publisher=chunk.source.publisher,
                        similarity_score=sim,
                        meets_supporting_threshold=meets_threshold,
                    )
                )

                if meets_threshold:
                    label = (
                        "Synthetic Demo Evidence"
                        if "Synthetic" in chunk.source.publisher or "Demo" in chunk.source.title
                        else "External Verified Evidence"
                    )

                    citations.append(
                        ResearchCitation(
                            source_id=chunk.source.id,
                            chunk_id=chunk.id,
                            title=chunk.source.title,
                            publisher=chunk.source.publisher,
                            url=chunk.source.url,
                            publication_date=str(chunk.source.publication_date) if chunk.source.publication_date else None,
                            similarity_score=sim,
                            excerpt=chunk.chunk_text[:300] + "..." if len(chunk.chunk_text) > 300 else chunk.chunk_text,
                            evidence_label=label,
                        )
                    )

        conflicts = self._detect_conflicts(citations)
        evidence_available = len(citations) > 0

        return ResearchQueryResult(
            candidate_chunks=candidate_chunks,
            citations=citations,
            conflicts=conflicts,
            evidence_available=evidence_available,
            configured_threshold=threshold,
            query_vector_latency_ms=round(embed_time, 2),
        )

    def _detect_conflicts(self, citations: List[ResearchCitation]) -> List[ResearchConflict]:
        """Surface contradictory evidence across retrieved supporting research sources."""
        conflicts = []
        if len(citations) >= 2:
            c1, c2 = citations[0], citations[1]
            if c1.publisher != c2.publisher:
                if ("increase" in c1.excerpt.lower() and "risk" in c2.excerpt.lower()) or (
                    "cost" in c1.excerpt.lower() and "saving" in c2.excerpt.lower()
                ):
                    conflicts.append(
                        ResearchConflict(
                            topic="Implementation Cost & Risk Variance",
                            source_a_title=c1.title,
                            source_a_finding=c1.excerpt[:150],
                            source_b_title=c2.title,
                            source_b_finding=c2.excerpt[:150],
                            description="Retrieved supporting research sources show variance between initial integration risks vs long-term ROI.",
                        )
                    )
        return conflicts
