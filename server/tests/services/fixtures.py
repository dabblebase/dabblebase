"""Fixtures used for testing core services."""

import pytest
from ...services import (
    AssignmentService,
    CourseService,
    HealthService,
    ProjectAuthService,
    ProjectService,
)
from ...services.content_db_cluster import ContentDbClusterService
from sqlalchemy import Engine
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


@pytest.fixture()
def course_svc(
    admin_db_session: Session,
    content_db_session: Session,
    test_content_engine: Engine,
) -> CourseService:
    cluster_db_service = ContentDbClusterService(
        content_db_session, test_content_engine
    )
    return CourseService(admin_db_session, cluster_db_service)


@pytest.fixture()
def assignment_svc(
    admin_db_session: Session,
    content_db_session: Session,
    test_content_engine: Engine,
) -> AssignmentService:
    cluster_db_service = ContentDbClusterService(
        content_db_session, test_content_engine
    )
    return AssignmentService(
        admin_db_session,
        CourseService(admin_db_session, cluster_db_service),
        cluster_db_service,
    )
