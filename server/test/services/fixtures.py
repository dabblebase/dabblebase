"""Fixtures used for testing core services."""

import pytest
from ...services import HealthService


@pytest.fixture()
def health_svc() -> HealthService:
    return HealthService()
