"""Unit tests for Phase 2 Pydantic schemas."""

import uuid
import pytest
from pydantic import ValidationError

from app.schemas.activity import ActivityCreate
from app.schemas.ai_opportunity import AIOpportunityCreate
from app.schemas.governance import GovernanceCreate
from app.schemas.organisation import OrganisationCreate
from app.schemas.process import ProcessCreate
from app.schemas.strategy import StrategyCreate


def test_organisation_schema_valid():
    org = OrganisationCreate(
        name="NovaMart",
        industry="Retail",
        description="Retail chain",
    )
    assert org.name == "NovaMart"
    assert org.is_active is True


def test_organisation_schema_invalid_empty_name():
    with pytest.raises(ValidationError):
        OrganisationCreate(name="")


def test_strategy_schema_valid():
    org_id = uuid.uuid4()
    strat = StrategyCreate(
        organisation_id=org_id,
        name="AI Growth Strategy",
        status="active",
    )
    assert strat.organisation_id == org_id
    assert strat.status == "active"


def test_strategy_schema_invalid_status():
    with pytest.raises(ValidationError):
        StrategyCreate(
            organisation_id=uuid.uuid4(),
            name="Test",
            status="invalid_status",  # type: ignore[arg-type]
        )


def test_process_schema_valid():
    proc = ProcessCreate(
        organisation_id=uuid.uuid4(),
        value_chain_id=uuid.uuid4(),
        name="Demand Forecasting",
        process_type="operational",
        status="active",
    )
    assert proc.process_type == "operational"


def test_ai_opportunity_schema_valid():
    opp = AIOpportunityCreate(
        organisation_id=uuid.uuid4(),
        name="Dynamic Pricing",
        category="optimization",
        status="identified",
    )
    assert opp.category == "optimization"


def test_governance_schema_valid():
    gov = GovernanceCreate(
        ai_opportunity_id=uuid.uuid4(),
        category="privacy",
        risk_level="high",
        description="PII handling",
    )
    assert gov.risk_level == "high"
    assert gov.category == "privacy"
