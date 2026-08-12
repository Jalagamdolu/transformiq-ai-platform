"""Research Ingestion Service.

Validates URLs against approved domain allowlists, enforces untrusted content safety,
and ingests research documents into PostgreSQL pgvector chunks.
"""

from __future__ import annotations

import hashlib
import logging
from typing import List, Optional, Tuple
from urllib.parse import urlparse
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DocumentChunk, ResearchSource
from app.rag.chunker import RecursiveTextChunker
from app.rag.embeddings import get_embedding_provider

logger = logging.getLogger(__name__)

# Approved domain allowlist for research ingestion security
ALLOWED_RESEARCH_DOMAINS = {
    "mckinsey.com",
    "www.mckinsey.com",
    "gartner.com",
    "www.gartner.com",
    "arxiv.org",
    "www.arxiv.org",
    "hbr.org",
    "www.hbr.org",
    "retail-ai-research.org",
    "www.retail-ai-research.org",
    "synthetic.local",
}


class ResearchIngestionService:
    """Ingests, chunks, embeds, and stores research documents safely."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.chunker = RecursiveTextChunker(chunk_size=500, chunk_overlap=50)
        self.embedder = get_embedding_provider()

    @staticmethod
    def validate_url(url: str) -> bool:
        """Validate URL against approved domain allowlist to prevent SSRF."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            return domain in ALLOWED_RESEARCH_DOMAINS
        except Exception:
            return False

    async def ingest_research_document(
        self,
        title: str,
        publisher: str,
        url: str,
        content: str,
        source_type: str = "industry_report",
        organisation_id: Optional[UUID] = None,
        publication_date: Optional[Any] = None,
        credibility_metadata: Optional[dict] = None,
    ) -> Tuple[ResearchSource, int]:
        """Ingest document, split into chunks, embed via pgvector, and save to database.

        Returns:
            Tuple of (ResearchSource, chunks_count)
        """
        # 1. URL Allowlist Security Check
        if not self.validate_url(url):
            raise ValueError(
                f"Security Violation: URL domain for '{url}' is not in approved allowlist {ALLOWED_RESEARCH_DOMAINS}."
            )

        # 2. Content Hash Check for duplicate prevention
        content_hash = hashlib.sha256(content.encode("utf-8")).hexdigest()

        stmt = select(ResearchSource).where(ResearchSource.content_hash == content_hash)
        res = await self.session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            logger.info("Research document '%s' already ingested (hash: %s).", title, content_hash[:8])
            return existing, len(existing.chunks)

        # 3. Create ResearchSource
        source = ResearchSource(
            organisation_id=organisation_id,
            title=title,
            publisher=publisher,
            url=url,
            source_type=source_type,
            publication_date=publication_date,
            content_hash=content_hash,
            credibility_metadata=credibility_metadata or {},
        )
        self.session.add(source)
        await self.session.flush()

        # 4. Chunk Document
        chunk_specs = self.chunker.chunk_document(
            source_id=source.id,
            text=content,
            base_metadata={
                "title": title,
                "publisher": publisher,
                "url": url,
            },
        )

        # 5. Embed and Save Chunks
        for spec in chunk_specs:
            vec = self.embedder.embed_text(spec.chunk_text)
            doc_chunk = DocumentChunk(
                source_id=source.id,
                chunk_index=spec.chunk_index,
                chunk_text=spec.chunk_text,
                metadata_json=spec.metadata,
                embedding=vec,
            )
            self.session.add(doc_chunk)

        await self.session.commit()
        return source, len(chunk_specs)
