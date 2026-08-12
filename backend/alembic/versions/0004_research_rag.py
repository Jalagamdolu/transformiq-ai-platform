"""0004_research_rag

Revision ID: 0004
Revises: 0003
Create Date: 2026-08-12 11:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from pgvector.sqlalchemy import Vector

# revision identifiers, used by Alembic.
revision: str = '0004'
down_revision: Union[str, None] = '0003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. research_sources
    op.create_table(
        'research_sources',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organisation_id', sa.UUID(), nullable=True),
        sa.Column('title', sa.String(length=512), nullable=False),
        sa.Column('publisher', sa.String(length=255), nullable=False),
        sa.Column('url', sa.Text(), nullable=False),
        sa.Column('source_type', sa.String(length=50), server_default='industry_report', nullable=False),
        sa.Column('publication_date', sa.Date(), nullable=True),
        sa.Column('retrieved_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('credibility_metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('content_hash')
    )
    op.create_index(op.f('ix_research_sources_content_hash'), 'research_sources', ['content_hash'], unique=True)
    op.create_index(op.f('ix_research_sources_organisation_id'), 'research_sources', ['organisation_id'], unique=False)

    # 2. document_chunks
    op.create_table(
        'document_chunks',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('source_id', sa.UUID(), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('chunk_text', sa.Text(), nullable=False),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['source_id'], ['research_sources.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_document_chunks_source_id'), 'document_chunks', ['source_id'], unique=False)

    # HNSW Index for document_chunks
    op.execute(
        "CREATE INDEX idx_document_chunks_embedding ON document_chunks USING hnsw (embedding vector_cosine_ops);"
    )

    # 3. enterprise_entity_embeddings
    op.create_table(
        'enterprise_entity_embeddings',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('organisation_id', sa.UUID(), nullable=False),
        sa.Column('entity_type', sa.String(length=50), nullable=False),
        sa.Column('entity_id', sa.UUID(), nullable=False),
        sa.Column('searchable_text', sa.Text(), nullable=False),
        sa.Column('content_hash', sa.String(length=64), nullable=False),
        sa.Column('embedding_model', sa.String(length=100), server_default='all-MiniLM-L6-v2', nullable=False),
        sa.Column('embedding_model_version', sa.String(length=20), server_default='1.0.0', nullable=False),
        sa.Column('embedding', Vector(384), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['organisation_id'], ['organisations.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_enterprise_entity_embeddings_content_hash'), 'enterprise_entity_embeddings', ['content_hash'], unique=False)
    op.create_index(op.f('ix_enterprise_entity_embeddings_entity_id'), 'enterprise_entity_embeddings', ['entity_id'], unique=False)
    op.create_index(op.f('ix_enterprise_entity_embeddings_entity_type'), 'enterprise_entity_embeddings', ['entity_type'], unique=False)
    op.create_index(op.f('ix_enterprise_entity_embeddings_organisation_id'), 'enterprise_entity_embeddings', ['organisation_id'], unique=False)

    # HNSW Index for enterprise_entity_embeddings
    op.execute(
        "CREATE INDEX idx_enterprise_entity_embeddings ON enterprise_entity_embeddings USING hnsw (embedding vector_cosine_ops);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS idx_enterprise_entity_embeddings;")
    op.drop_index(op.f('ix_enterprise_entity_embeddings_organisation_id'), table_name='enterprise_entity_embeddings')
    op.drop_index(op.f('ix_enterprise_entity_embeddings_entity_type'), table_name='enterprise_entity_embeddings')
    op.drop_index(op.f('ix_enterprise_entity_embeddings_entity_id'), table_name='enterprise_entity_embeddings')
    op.drop_index(op.f('ix_enterprise_entity_embeddings_content_hash'), table_name='enterprise_entity_embeddings')
    op.drop_table('enterprise_entity_embeddings')

    op.execute("DROP INDEX IF EXISTS idx_document_chunks_embedding;")
    op.drop_index(op.f('ix_document_chunks_source_id'), table_name='document_chunks')
    op.drop_table('document_chunks')

    op.drop_index(op.f('ix_research_sources_organisation_id'), table_name='research_sources')
    op.drop_index(op.f('ix_research_sources_content_hash'), table_name='research_sources')
    op.drop_table('research_sources')
