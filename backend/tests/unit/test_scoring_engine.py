"""Unit tests for the Scoring Engine."""

import pytest
from app.engines.scoring_engine import ScoringEngine, DEFAULT_FACTOR_WEIGHTS


def test_scoring_weights_sum_to_one():
    engine = ScoringEngine()
    assert sum(engine.weights.values()) == pytest.approx(1.0)


def test_invalid_weights_raise_error():
    with pytest.raises(ValueError, match="must sum to 1.0"):
        ScoringEngine(weights={"strategic_alignment": 0.5})


def test_scoring_calculation_high_priority():
    engine = ScoringEngine()
    affected_entities = {
        "processes": [{"id": "1"}, {"id": "2"}],
        "roles": [{"id": "r1"}, {"id": "r2"}, {"id": "r3"}],
        "skills": [{"id": "s1"}, {"id": "s2"}, {"id": "s3"}, {"id": "s4"}],
        "transformation_initiatives": [{"id": "i1"}],
    }
    governance_findings = []
    dependency_findings = {"upstream_prerequisites": [], "downstream_dependents": [], "has_cycles": False}

    score, category, factor_details, reason_codes = engine.evaluate_scenario(
        affected_entities=affected_entities,
        governance_findings=governance_findings,
        dependency_findings=dependency_findings,
        opportunity_status="approved",
        ai_technology="Transformer",
    )

    assert score >= 75.0
    assert category == "HIGH"
    assert "strategic_alignment" in factor_details
    assert factor_details["strategic_alignment"]["weighted_score"] > 0


def test_scoring_risk_inversion():
    """Verify high risk raw score reduces overall score (raw score 100 -> effective score 0)."""
    engine = ScoringEngine()
    affected_entities = {}
    high_risk_gov = [{"risk_level": "critical"}, {"risk_level": "high"}, {"risk_level": "high"}]
    dependency_findings = {}

    score, category, factor_details, _ = engine.evaluate_scenario(
        affected_entities=affected_entities,
        governance_findings=high_risk_gov,
        dependency_findings=dependency_findings,
    )

    risk_factor = factor_details["risk"]
    assert risk_factor["score"] >= 80.0  # Raw risk is high
    assert risk_factor["weighted_score"] <= 2.0  # Inverted weighted contribution is low
