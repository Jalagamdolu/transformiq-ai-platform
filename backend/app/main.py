"""FastAPI application factory.

Creates and configures the FastAPI application instance with middleware,
routers, and exception handlers.
"""

from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import generic_exception_handler
from app.api.v1.router import api_router

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """Construct and configure the FastAPI application."""

    application = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description=(
            "Enterprise Transformation Intelligence Platform — "
            "AI-powered analysis for organisational AI transformation."
        ),
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # ── Middleware ────────────────────────────────────────────────────────────
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.backend_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────────────────────────────
    application.add_exception_handler(Exception, generic_exception_handler)

    # ── Routers ───────────────────────────────────────────────────────────────
    application.include_router(api_router, prefix="/api/v1")

    # ── Root endpoint ─────────────────────────────────────────────────────────
    @application.get("/", tags=["root"], include_in_schema=False)
    async def root() -> dict:
        return {
            "name": settings.app_name,
            "version": settings.app_version,
            "docs": "/docs",
            "health": "/api/v1/health",
        }

    logger.info(
        "TransformIQ API initialised | env=%s | debug=%s",
        settings.environment,
        settings.debug,
    )

    return application


app = create_application()
