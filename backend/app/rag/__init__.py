"""RAG (Retrieval-Augmented Generation) package (Phase 2+).

This package will contain:
  - retriever.py   — Semantic similarity search via pgvector
  - chunker.py     — Document chunking strategies
  - indexer.py     — Embed and store documents in pgvector

pgvector is used exclusively for research/evidence retrieval in the RAG layer.
Individual enterprise entities (processes, activities) do NOT get embeddings
unless a specific retrieval requirement justifies it.
No RAG code is active in Phase 1.
"""
