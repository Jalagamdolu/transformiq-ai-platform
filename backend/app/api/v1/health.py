"""Health check endpoint.

GET /api/v1/health

Returns the operational status of the API and its database connection.
The database check is best-effort — the endpoint always returns 200 so that
load balancers and uptime monitors can distinguish an unreachable service
(connection refused / 5xx) from a running service with a degraded dependency.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.dependencies import get_db
from app.schemas.common import HealthResponse

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "",
    response_model=HealthResponse,
    summary="System health check",
    description=(
        "Returns API status and database connectivity. "
        "Always returns HTTP 200; check the `database` field for DB status."
    ),
)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Verify that the API is running and the database is reachable."""
    db_status = "unreachable"
    try:
        await db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception as exc:  # noqa: BLE001
        logger.warning("Database health check failed: %s", exc)

    return HealthResponse(
        status="ok",
        version="0.1.0",
        environment="development",
        database=db_status,
    )
