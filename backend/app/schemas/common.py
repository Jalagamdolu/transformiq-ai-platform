"""Common / shared Pydantic schemas used across multiple endpoints."""

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


# =============================================================================
# Health
# =============================================================================


class HealthResponse(BaseModel):
    """Response schema for GET /api/v1/health."""

    status: str = Field(..., examples=["ok"])
    version: str = Field(..., examples=["0.1.0"])
    environment: str = Field(..., examples=["development"])
    database: str = Field(..., examples=["connected", "unreachable"])


# =============================================================================
# Generic Pagination
# =============================================================================


class PaginatedResponse(BaseModel, Generic[DataT]):
    """Generic paginated list response.

    Usage:
        @router.get("/items", response_model=PaginatedResponse[ItemResponse])
    """

    items: List[DataT]
    total: int = Field(..., description="Total number of records matching the query")
    skip: int = Field(0, description="Number of skipped items")
    limit: int = Field(20, description="Items per page limit")

    @classmethod
    def create(
        cls, items: List[DataT], total: int, skip: int, limit: int
    ) -> "PaginatedResponse[DataT]":
        return cls(items=items, total=total, skip=skip, limit=limit)


# =============================================================================
# Errors
# =============================================================================


class ErrorResponse(BaseModel):
    """Standard error response body."""

    detail: str = Field(..., description="Human-readable error message")
    code: Optional[str] = Field(None, description="Machine-readable error code")
