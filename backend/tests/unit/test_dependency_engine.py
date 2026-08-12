"""Unit tests for Dependency Engine validation and cycle detection."""

import uuid
import pytest
from app.engines.dependency_engine import DependencyEngine


def test_self_dependency_validation_fails():
    entity_id = uuid.uuid4()
    with pytest.raises(ValueError, match="Self-dependency is not allowed"):
        DependencyEngine.validate_dependency_creation(
            source_entity_type="opportunity",
            source_entity_id=entity_id,
            target_entity_type="opportunity",
            target_entity_id=entity_id,
        )


def test_different_entities_validation_passes():
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    # Should not raise exception
    DependencyEngine.validate_dependency_creation(
        source_entity_type="opportunity",
        source_entity_id=id1,
        target_entity_type="opportunity",
        target_entity_id=id2,
    )
