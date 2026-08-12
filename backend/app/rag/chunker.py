"""Text Chunker module for Phase 4B RAG pipeline.

Splits research documents into overlapping text chunks while preserving metadata.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ChunkSpec(BaseModel):
    """Specification of an individual document chunk."""

    model_config = ConfigDict(extra="forbid")

    source_id: UUID
    chunk_index: int
    chunk_text: str
    char_start: int
    char_end: int
    metadata: Dict[str, Any]


class RecursiveTextChunker:
    """Chunks text documents into overlapping segments preserving metadata."""

    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        source_id: UUID,
        text: str,
        base_metadata: Optional[Dict[str, Any]] = None,
    ) -> List[ChunkSpec]:
        """Split document text into overlapping ChunkSpec items."""
        if not text or not text.strip():
            return []

        clean_text = text.strip()
        metadata = base_metadata or {}
        chunks: List[ChunkSpec] = []

        start = 0
        text_len = len(clean_text)
        chunk_idx = 0

        while start < text_len:
            end = min(start + self.chunk_size, text_len)

            # Try to snap to sentence or paragraph break if within range
            if end < text_len:
                last_period = clean_text.rfind(".", start, end)
                if last_period > start + (self.chunk_size // 2):
                    end = last_period + 1

            chunk_str = clean_text[start:end].strip()

            if chunk_str:
                chunk_meta = {
                    **metadata,
                    "chunk_index": chunk_idx,
                    "length": len(chunk_str),
                }
                chunks.append(
                    ChunkSpec(
                        source_id=source_id,
                        chunk_index=chunk_idx,
                        chunk_text=chunk_str,
                        char_start=start,
                        char_end=end,
                        metadata=chunk_meta,
                    )
                )
                chunk_idx += 1

            if end >= text_len:
                break

            start = max(end - self.chunk_overlap, start + 1)

        return chunks
