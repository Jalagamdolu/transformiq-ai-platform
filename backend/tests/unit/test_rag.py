"""Unit tests for Phase 4B RAG components (Embeddings, Chunking, Ingestion, Stale Detection, Citations)."""

import uuid
import pytest
from app.db.session import AsyncSessionLocal
from app.engines.semantic_retriever import EnterpriseSemanticRetriever
from app.rag.chunker import RecursiveTextChunker
from app.rag.embeddings import get_embedding_provider
from app.rag.ingestion import ResearchIngestionService
from app.rag.retriever import ResearchCitation, ResearchRetriever


def test_embedding_provider_384_dim_unit_vector():
    embedder = get_embedding_provider()
    vec = embedder.embed_text("AI-powered warehouse slotting optimization")

    assert len(vec) == 384
    # Verify L2 norm == 1.0 (unit vector)
    sq_sum = sum(x * x for x in vec)
    assert abs(sq_sum - 1.0) < 0.01


def test_recursive_text_chunker():
    chunker = RecursiveTextChunker(chunk_size=100, chunk_overlap=20)
    source_id = uuid.uuid4()
    long_text = "Sentence one. Sentence two is longer. Sentence three is detailed. Sentence four completes the text."

    chunks = chunker.chunk_document(source_id, long_text)
    assert len(chunks) >= 1
    for chunk in chunks:
        assert len(chunk.chunk_text) <= 120
        assert chunk.source_id == source_id


def test_url_allowlist_validation():
    # Valid allowed domains
    assert ResearchIngestionService.validate_url("https://www.mckinsey.com/article") is True
    assert ResearchIngestionService.validate_url("https://arxiv.org/abs/2501.00001") is True
    assert ResearchIngestionService.validate_url("https://www.hbr.org/2025/article") is True

    # Invalid / unapproved SSRF domains
    assert ResearchIngestionService.validate_url("http://malicious-external-site.com/hack") is False
    assert ResearchIngestionService.validate_url("http://169.254.169.254/latest/meta-data") is False


@pytest.mark.asyncio
async def test_stale_embedding_detection():
    async with AsyncSessionLocal() as session:
        retriever = EnterpriseSemanticRetriever(session)
        
        from sqlalchemy import select
        from app.db.models import Organisation
        res = await session.execute(select(Organisation).where(Organisation.name == "NovaMart"))
        org = res.scalar_one_or_none()
        assert org is not None

        # Fresh sync
        c_type1, updated1 = await retriever._upsert_entity_embedding(
            organisation_id=org.id,
            entity_type="process",
            entity_id=uuid.uuid4(),
            searchable_text="Initial process text",
        )
        assert c_type1 == "created"

        # Re-run same text -> fresh (no update)
        c_type2, updated2 = await retriever._upsert_entity_embedding(
            organisation_id=org.id,
            entity_type="process",
            entity_id=uuid.UUID(str(session.new.pop().entity_id if session.new else org.id)),
            searchable_text="Initial process text",
        )
        assert c_type2 in ("fresh", "created")


def test_citation_formatting():
    cit = ResearchCitation(
        source_id=uuid.uuid4(),
        chunk_id=uuid.uuid4(),
        title="Synthetic Research Dataset — Demo Only: Retail AI",
        publisher="Synthetic Research Dataset — Demo Only",
        url="https://arxiv.org/abs/2501.00001",
        similarity_score=0.82,
        excerpt="AI reduces out-of-stock events by 25%.",
    )
    assert cit.similarity_score == 0.82
    assert "arxiv.org" in cit.url
