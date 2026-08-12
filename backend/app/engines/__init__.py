"""Business logic engines package (Phase 2+).

This package will contain:
  - impact_engine.py        — Calculates transformation impact per entity
  - scoring_engine.py       — Transformation Priority Score (multi-factor, configurable)
  - intelligence_engine.py  — Orchestrates AI + RAG + engines for full analysis

RULE: Engines must have NO knowledge of HTTP or database internals.
They accept plain data objects (Pydantic models / dataclasses) and return results.
This makes them fully unit-testable without any running services.
"""
