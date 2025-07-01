"""Fixtures used for testing core services."""

import pytest
from ...services import HealthService, ProjectService, ProjectAuthService
from sqlalchemy.orm import Session


@pytest.fixture()
def health_svc(admin_db_session: Session, content_db_session: Session) -> HealthService:
    return HealthService(admin_db_session, content_db_session)


@pytest.fixture()
def project_svc(admin_db_session: Session) -> ProjectService:
    return ProjectService(admin_db_session)


@pytest.fixture()
def project_auth_svc(admin_db_session: Session) -> ProjectAuthService:
    return ProjectAuthService(admin_db_session)
