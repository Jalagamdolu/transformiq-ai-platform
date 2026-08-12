"""Async SQLAlchemy session factory.

Creates an async engine and session factory from the configured DATABASE_URL.
Import `AsyncSessionLocal` to create sessions, or use the `get_db` dependency.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.pool import NullPool

from app.core.config import settings

# In testing mode, use NullPool so connections are opened/closed per-session
# and never leaked across different asyncio event loops during pytest.
pool_kwargs = {}
if settings.environment.lower() == "testing":
    pool_kwargs["poolclass"] = NullPool

# The async engine — one per process.
engine = create_async_engine(
    settings.database_url,
    # Echo SQL statements in debug mode (very verbose in production)
    echo=settings.debug,
    future=True,
    # Proactively check for dead connections before handing them out
    pool_pre_ping=True,
    # asyncpg: fail fast if DB is unreachable (default is no timeout = hangs forever)
    connect_args={"timeout": 5},
    **pool_kwargs,
)

# Session factory — call AsyncSessionLocal() to create a new session.
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)
