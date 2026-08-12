"""Synthetic Research Seed Dataset for Phase 4B.

Populates demo research sources clearly labeled as 'Synthetic Research Dataset — Demo Only'
and syncs enterprise entity vector embeddings into PostgreSQL pgvector.
"""

from __future__ import annotations

import logging
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Organisation, ResearchSource
from app.engines.semantic_retriever import EnterpriseSemanticRetriever
from app.rag.ingestion import ResearchIngestionService

logger = logging.getLogger(__name__)


DEMO_RESEARCH_DOCUMENTS = [
    {
        "title": "Synthetic Research Dataset — Demo Only: Retail Supply Chain AI Optimization",
        "publisher": "Synthetic Research Dataset — Demo Only",
        "url": "https://arxiv.org/abs/2501.00001",
        "source_type": "preprint",
        "content": (
            "Deploying artificial intelligence models for automated supplier risk assessment, "
            "demand forecasting, and warehouse slotting optimization reduces retail out-of-stock events "
            "by 22% to 35%. Automated lead time tracking allows demand planners and supply chain analysts "
            "to preemptively re-route PO shipments before warehouse capacity constraints are breached."
        ),
    },
    {
        "title": "Synthetic Research Dataset — Demo Only: Automated Warehouse Slotting & Inventory Optimization",
        "publisher": "Synthetic Research Dataset — Demo Only",
        "url": "https://www.retail-ai-research.org/reports/warehouse-slotting-2025",
        "source_type": "industry_report",
        "content": (
            "Warehouse slotting optimization algorithms organize fast-moving retail SKUs near shipping docks "
            "using historical order frequency and dimensional characteristics. Integrating slotting analytics "
            "with store inventory management processes increases order picking throughput by 18% "
            "while reducing travel time for warehouse inventory controllers."
        ),
    },
    {
        "title": "Synthetic Research Dataset — Demo Only: Governance & Risk Management in Retail Machine Learning",
        "publisher": "Synthetic Research Dataset — Demo Only",
        "url": "https://www.hbr.org/2025/01/retail-ai-governance-framework",
        "source_type": "peer_reviewed",
        "content": (
            "Autonomous purchase order replenishment systems require strict financial governance guardrails. "
            "High-risk autonomous ordering models should enforce vendor caps ($50,000 threshold) and "
            "feature explainability dashboards (SHAP summaries) to ensure human-in-the-loop oversight."
        ),
    },
]


async def seed_research_data(session: AsyncSession, organisation: Optional[Organisation] = None) -> None:
    """Seed synthetic research documents and sync enterprise vector embeddings."""
    logger.info("Seeding Phase 4B synthetic research documents and enterprise embeddings...")

    # 1. Sync Enterprise Entity Embeddings for organisation if provided
    if organisation:
        semantic_retriever = EnterpriseSemanticRetriever(session)
        sync_counts = await semantic_retriever.sync_enterprise_embeddings(organisation.id)
        logger.info("Synced enterprise vector embeddings for %s: %s", organisation.name, sync_counts)

    # 2. Ingest Synthetic Research Documents
    ingestion_service = ResearchIngestionService(session)
    for doc in DEMO_RESEARCH_DOCUMENTS:
        try:
            source, count = await ingestion_service.ingest_research_document(
                title=doc["title"],
                publisher=doc["publisher"],
                url=doc["url"],
                content=doc["content"],
                source_type=doc["source_type"],
                organisation_id=None,  # Global demo research source
                credibility_metadata={"demo_dataset": True, "label": "Synthetic Research Dataset — Demo Only"},
            )
            logger.info("Ingested research source '%s' with %d chunks.", source.title[:50], count)
        except Exception as exc:
            logger.warning("Skipping research doc ingestion: %s", exc)
