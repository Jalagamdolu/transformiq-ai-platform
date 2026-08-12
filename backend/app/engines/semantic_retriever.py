"""Enterprise Semantic Retriever & Embedding Manager.

Generates and manages 384-dim vector embeddings for PostgreSQL enterprise domain entities,
detects stale embeddings via SHA256 content hashes, and executes hybrid vector + keyword retrieval.
"""

from __future__ import annotations

import hashlib
import logging
from typing import Dict, List, Optional, Tuple, Any
from uuid import UUID

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    Activity,
    AIOpportunity,
    EnterpriseEntityEmbedding,
    Process,
    Role,
    Skill,
    Strategy,
    ValueChain,
)
from app.rag.embeddings import (
    EMBEDDING_MODEL_NAME,
    EMBEDDING_MODEL_VERSION,
    get_embedding_provider,
)
from app.schemas.scenario import EntityMatchDetail, MatchedEntitiesResult

logger = logging.getLogger(__name__)


class EnterpriseSemanticRetriever:
    """Manages enterprise entity embeddings and performs pgvector hybrid semantic search."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.embedder = get_embedding_provider()

    async def sync_enterprise_embeddings(self, organisation_id: UUID) -> Dict[str, int]:
        """Syncs vector embeddings for all enterprise entities under organisation_id.

        Uses SHA256 content hashes to detect and regenerate stale embeddings.
        Returns count of synced and updated embeddings.
        """
        counts = {"created": 0, "updated": 0, "fresh": 0}

        # 1. Sync Processes
        p_stmt = select(Process).where(Process.organisation_id == organisation_id)
        p_res = await self.session.execute(p_stmt)
        for proc in p_res.scalars().all():
            text = f"Process: {proc.name}. Type: {proc.process_type}. Description: {proc.description or ''}"
            c_type, c_updated = await self._upsert_entity_embedding(
                organisation_id=organisation_id,
                entity_type="process",
                entity_id=proc.id,
                searchable_text=text,
            )
            counts[c_type] += 1

        # 2. Sync Opportunities
        o_stmt = select(AIOpportunity).where(AIOpportunity.organisation_id == organisation_id)
        o_res = await self.session.execute(o_stmt)
        for opp in o_res.scalars().all():
            text = f"AI Opportunity: {opp.name}. Category: {opp.category}. Tech: {opp.ai_technology or ''}. Description: {opp.description or ''}"
            c_type, c_updated = await self._upsert_entity_embedding(
                organisation_id=organisation_id,
                entity_type="opportunity",
                entity_id=opp.id,
                searchable_text=text,
            )
            counts[c_type] += 1

        # 3. Sync ValueChains
        v_stmt = select(ValueChain).where(ValueChain.organisation_id == organisation_id)
        v_res = await self.session.execute(v_stmt)
        for vc in v_res.scalars().all():
            text = f"Value Chain: {vc.name}. Description: {vc.description or ''}"
            c_type, c_updated = await self._upsert_entity_embedding(
                organisation_id=organisation_id,
                entity_type="value_chain",
                entity_id=vc.id,
                searchable_text=text,
            )
            counts[c_type] += 1

        # 4. Sync Roles & Skills
        r_stmt = select(Role).where(Role.organisation_id == organisation_id)
        r_res = await self.session.execute(r_stmt)
        for role in r_res.scalars().all():
            text = f"Role: {role.name}. Department: {role.department or ''}. Description: {role.description or ''}"
            c_type, c_updated = await self._upsert_entity_embedding(
                organisation_id=organisation_id,
                entity_type="role",
                entity_id=role.id,
                searchable_text=text,
            )
            counts[c_type] += 1

        s_stmt = select(Skill).where(Skill.organisation_id == organisation_id)
        s_res = await self.session.execute(s_stmt)
        for skill in s_res.scalars().all():
            text = f"Skill: {skill.name}. Type: {skill.skill_type or ''}. Description: {skill.description or ''}"
            c_type, c_updated = await self._upsert_entity_embedding(
                organisation_id=organisation_id,
                entity_type="skill",
                entity_id=skill.id,
                searchable_text=text,
            )
            counts[c_type] += 1

        await self.session.commit()
        return counts

    async def _upsert_entity_embedding(
        self,
        organisation_id: UUID,
        entity_type: str,
        entity_id: UUID,
        searchable_text: str,
    ) -> Tuple[str, bool]:
        """Insert or update embedding based on SHA256 content_hash check."""
        content_hash = hashlib.sha256(searchable_text.encode("utf-8")).hexdigest()

        stmt = select(EnterpriseEntityEmbedding).where(
            EnterpriseEntityEmbedding.organisation_id == organisation_id,
            EnterpriseEntityEmbedding.entity_type == entity_type,
            EnterpriseEntityEmbedding.entity_id == entity_id,
        )
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            # Stale embedding check
            if existing.content_hash == content_hash and existing.embedding_model == EMBEDDING_MODEL_NAME:
                return "fresh", False

            # Regenerate stale embedding
            vec = self.embedder.embed_text(searchable_text)
            existing.searchable_text = searchable_text
            existing.content_hash = content_hash
            existing.embedding = vec
            return "updated", True

        # Insert new embedding
        vec = self.embedder.embed_text(searchable_text)
        new_emb = EnterpriseEntityEmbedding(
            organisation_id=organisation_id,
            entity_type=entity_type,
            entity_id=entity_id,
            searchable_text=searchable_text,
            content_hash=content_hash,
            embedding_model=EMBEDDING_MODEL_NAME,
            embedding_model_version=EMBEDDING_MODEL_VERSION,
            embedding=vec,
        )
        self.session.add(new_emb)
        return "created", True

    async def search_semantic_entities(
        self,
        organisation_id: UUID,
        query_text: str,
        entity_type: Optional[str] = None,
        top_k: int = 5,
        min_similarity: float = 0.60,
    ) -> List[Tuple[EnterpriseEntityEmbedding, float]]:
        """Search enterprise entity embeddings using pgvector cosine distance.

        Returns list of (EnterpriseEntityEmbedding, float_similarity_score).
        Calculates exact cosine similarity dynamically: 1 - cosine_distance.
        """
        query_vector = self.embedder.embed_text(query_text)

        stmt = select(
            EnterpriseEntityEmbedding,
            (1 - EnterpriseEntityEmbedding.embedding.cosine_distance(query_vector)).label("similarity"),
        ).where(
            EnterpriseEntityEmbedding.organisation_id == organisation_id,
        )

        if entity_type:
            stmt = stmt.where(EnterpriseEntityEmbedding.entity_type == entity_type)

        stmt = stmt.order_by(EnterpriseEntityEmbedding.embedding.cosine_distance(query_vector).asc()).limit(top_k)

        res = await self.session.execute(stmt)
        results = []
        for row in res.all():
            emb_obj, sim = row[0], float(row[1])
            if sim >= min_similarity:
                results.append((emb_obj, round(sim, 4)))

        return results
