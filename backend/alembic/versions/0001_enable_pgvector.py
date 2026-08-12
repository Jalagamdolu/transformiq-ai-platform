"""Enable pgvector extension.

Revision ID: 0001
Revises: (none — initial migration)
Create Date: 2026-08-12

This is the first migration. It enables the pgvector PostgreSQL extension,
which is required for semantic similarity search in the RAG layer (Phase 2+).

The ankane/pgvector Docker image already has the extension compiled and
available — this migration just activates it for the database.
"""

from typing import Sequence, Union

from alembic import op

# ---------------------------------------------------------------------------
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
# ---------------------------------------------------------------------------


def upgrade() -> None:
    """Enable the pgvector extension."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Disable the pgvector extension.

    WARNING: This will drop ALL vector columns and indexes in the database.
    Only run this if you intend to fully remove vector support.
    """
    op.execute("DROP EXTENSION IF EXISTS vector CASCADE")
