"""Fixtures used for testing core services."""

import pytest
from ...services import HealthService
from sqlalchemy.orm import Session


@pytest.fixture()
def health_svc(admin_db_session: Session, content_db_session: Session) -> HealthService:
    return HealthService(admin_db_session, content_db_session)
