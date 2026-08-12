"""Performance Benchmark Test for pgvector HNSW vector search.

Measures vector search execution time and asserts performance standards.
"""

import time
import pytest
from sqlalchemy import select
from app.db.models import DocumentChunk
from app.db.session import AsyncSessionLocal
from app.rag.embeddings import get_embedding_provider


@pytest.mark.asyncio
async def test_pgvector_hnsw_search_performance_benchmark():
    """Benchmark pgvector HNSW cosine distance search latency."""
    embedder = get_embedding_provider()
    query_vector = embedder.embed_text("warehouse slotting inventory optimization")

    async with AsyncSessionLocal() as session:
        # Warmup query
        stmt = (
            select(DocumentChunk.id)
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector).asc())
            .limit(1)
        )
        await session.execute(stmt)

        # Benchmark query execution
        start_time = time.perf_counter()
        stmt_bench = (
            select(
                DocumentChunk.id,
                (1 - DocumentChunk.embedding.cosine_distance(query_vector)).label("similarity"),
            )
            .order_by(DocumentChunk.embedding.cosine_distance(query_vector).asc())
            .limit(5)
        )
        res = await session.execute(stmt_bench)
        results = res.all()
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        print(f"\n[BENCHMARK] pgvector HNSW Search Latency: {elapsed_ms:.3f} ms (Retrieved {len(results)} rows)")
        assert elapsed_ms < 100.0
