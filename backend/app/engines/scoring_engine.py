"""Deterministic Transformation Priority Scoring Engine.

Calculates a weighted Transformation Priority Score based on 7 factors:
1. Strategic Alignment (20%)
2. Business Value (20%)
3. AI Feasibility (15%)
4. Data Readiness (15%)
5. Expected Impact (15%)
6. Risk (10% — inverted, so lower risk yields a higher priority contribution)
7. Dependency Complexity (5% — inverted, lower complexity yields higher score)

Priority Categories:
  - HIGH:   Score >= 75.0
  - MEDIUM: 50.0 <= Score < 75.0
  - LOW:    Score < 50.0
"""

from __future__ import annotations

from typing import Any, Dict, List, Tuple

# Default weights (must sum to 1.0)
DEFAULT_FACTOR_WEIGHTS: Dict[str, float] = {
    "strategic_alignment": 0.20,
    "business_value": 0.20,
    "ai_feasibility": 0.15,
    "data_readiness": 0.15,
    "expected_impact": 0.15,
    "risk": 0.10,
    "dependency_complexity": 0.05,
}


class ScoringEngine:
    """Calculates priority scores and structured reason codes without LLMs."""

    def __init__(self, weights: Dict[str, float] | None = None) -> None:
        self.weights = weights or DEFAULT_FACTOR_WEIGHTS.copy()
        # Verify weights sum to 1.0
        total_weight = sum(self.weights.values())
        if not (0.99 <= total_weight <= 1.01):
            raise ValueError(f"Factor weights must sum to 1.0, got {total_weight:.4f}")

    def evaluate_scenario(
        self,
        affected_entities: Dict[str, Any],
        governance_findings: List[Dict[str, Any]],
        dependency_findings: Dict[str, Any],
        opportunity_status: str | None = None,
        ai_technology: str | None = None,
    ) -> Tuple[float, str, Dict[str, Any], Dict[str, Any]]:
        """Calculate score, category, factor details, and reason codes.

        Returns:
            (final_score, priority_category, factor_scores_dict, reason_codes_dict)
        """
        raw_scores, reason_codes = self._calculate_factor_raw_scores(
            affected_entities=affected_entities,
            governance_findings=governance_findings,
            dependency_findings=dependency_findings,
            opportunity_status=opportunity_status,
            ai_technology=ai_technology,
        )

        factor_details: Dict[str, Any] = {}
        total_weighted_score = 0.0

        for factor_name, weight in self.weights.items():
            raw_score = raw_scores.get(factor_name, 50.0)
            
            # Risk & Complexity are inverted for final weighted score
            # (Higher risk/complexity lowers the overall priority score)
            if factor_name in ("risk", "dependency_complexity"):
                effective_score = max(0.0, 100.0 - raw_score)
            else:
                effective_score = raw_score

            weighted_contrib = round(effective_score * weight, 2)
            total_weighted_score += weighted_contrib

            factor_details[factor_name] = {
                "score": round(raw_score, 1),
                "weight": weight,
                "weighted_score": weighted_contrib,
                "reason_codes": reason_codes.get(factor_name, []),
            }

        final_score = round(min(100.0, max(0.0, total_weighted_score)), 1)
        priority_category = self._classify_score(final_score)

        return final_score, priority_category, factor_details, reason_codes

    def _calculate_factor_raw_scores(
        self,
        affected_entities: Dict[str, Any],
        governance_findings: List[Dict[str, Any]],
        dependency_findings: Dict[str, Any],
        opportunity_status: str | None,
        ai_technology: str | None,
    ) -> Tuple[Dict[str, float], Dict[str, List[str]]]:
        raw_scores: Dict[str, float] = {}
        reason_codes: Dict[str, List[str]] = {}

        proc_count = len(affected_entities.get("processes", []))
        role_count = len(affected_entities.get("roles", []))
        skill_count = len(affected_entities.get("skills", []))
        init_count = len(affected_entities.get("transformation_initiatives", []))

        # 1. Strategic Alignment
        strat_score = 60.0
        strat_reasons = []
        if init_count > 0:
            strat_score += 25.0
            strat_reasons.append("SUPPORTS_ACTIVE_INITIATIVE")
        if proc_count >= 1:
            strat_score += 15.0
            strat_reasons.append("ALIGNS_WITH_CORE_VALUE_CHAIN_PROCESS")
        raw_scores["strategic_alignment"] = min(100.0, strat_score)
        reason_codes["strategic_alignment"] = strat_reasons or ["BASE_STRATEGIC_ALIGNMENT"]

        # 2. Business Value
        val_score = 50.0
        val_reasons = []
        if role_count >= 3:
            val_score += 25.0
            val_reasons.append("HIGH_ROLE_PRODUCTIVITY_IMPACT")
        if skill_count >= 4:
            val_score += 25.0
            val_reasons.append("BROAD_CAPABILITY_ENHANCEMENT")
        raw_scores["business_value"] = min(100.0, val_score)
        reason_codes["business_value"] = val_reasons or ["STANDARD_BUSINESS_VALUE"]

        # 3. AI Feasibility
        feas_score = 65.0
        feas_reasons = []
        if opportunity_status in ("approved", "in_progress"):
            feas_score += 25.0
            feas_reasons.append("APPROVED_AI_TECHNOLOGY_STACK")
        if ai_technology:
            feas_score += 10.0
            feas_reasons.append("DEFINED_AI_ARCHITECTURE")
        raw_scores["ai_feasibility"] = min(100.0, feas_score)
        reason_codes["ai_feasibility"] = feas_reasons or ["FEASIBLE_AI_MATURITY"]

        # 4. Data Readiness
        data_score = 70.0
        data_reasons = ["STRUCTURED_PROCESS_DATA_AVAILABLE"]
        raw_scores["data_readiness"] = data_score
        reason_codes["data_readiness"] = data_reasons

        # 5. Expected Impact
        impact_score = 40.0
        impact_reasons = []
        if proc_count >= 2 or role_count >= 2:
            impact_score += 30.0
            impact_reasons.append("MULTI_PROCESS_ORGANISATIONAL_IMPACT")
        if skill_count >= 2:
            impact_score += 30.0
            impact_reasons.append("WORKFORCE_SKILL_TRANSFORMATION")
        raw_scores["expected_impact"] = min(100.0, impact_score)
        reason_codes["expected_impact"] = impact_reasons or ["LOCALIZED_PROCESS_IMPACT"]

        # 6. Risk (Raw risk level: higher = more risk)
        high_risk_gov = sum(1 for g in governance_findings if g.get("risk_level") in ("high", "critical"))
        med_risk_gov = sum(1 for g in governance_findings if g.get("risk_level") == "medium")
        risk_score = 20.0 + (high_risk_gov * 30.0) + (med_risk_gov * 15.0)
        risk_reasons = []
        if high_risk_gov > 0:
            risk_reasons.append("HIGH_GOVERNANCE_RISK_DETECTED")
        if med_risk_gov > 0:
            risk_reasons.append("MODERATE_COMPLIANCE_REQUIREMENTS")
        raw_scores["risk"] = min(100.0, risk_score)
        reason_codes["risk"] = risk_reasons or ["LOW_GOVERNANCE_RISK"]

        # 7. Dependency Complexity
        upstream_count = len(dependency_findings.get("upstream_prerequisites", []))
        downstream_count = len(dependency_findings.get("downstream_dependents", []))
        has_cycles = dependency_findings.get("has_cycles", False)

        complexity_score = (upstream_count * 20.0) + (downstream_count * 15.0)
        complexity_reasons = []
        if upstream_count > 0:
            complexity_reasons.append("REQUIRES_UPSTREAM_PREREQUISITES")
        if downstream_count > 0:
            complexity_reasons.append("BLOCKS_DOWNSTREAM_INITIATIVES")
        if has_cycles:
            complexity_score += 40.0
            complexity_reasons.append("CIRCULAR_DEPENDENCY_DETECTED")
        raw_scores["dependency_complexity"] = min(100.0, complexity_score)
        reason_codes["dependency_complexity"] = complexity_reasons or ["NO_DEPENDENCY_BLOCKED"]

        return raw_scores, reason_codes

    @staticmethod
    def _classify_score(score: float) -> str:
        if score >= 75.0:
            return "HIGH"
        if score >= 50.0:
            return "MEDIUM"
        return "LOW"
