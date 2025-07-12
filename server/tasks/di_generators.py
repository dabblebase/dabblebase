"""
Since the Celery process runs indepedently of FastAPI, we cannot rely on
FastAPI's dependency injection system to provide injectible services.

So, this file manually constructs necessary services to use with Celery tasks.
"""

from ..services import AssignmentService, CourseService, ContentDbClusterService
from sqlalchemy.orm import Session
from ..database import admin_db_session, content_db_session, content_db_engine


def get_assignment_service() -> AssignmentService:
    """Manually constructs AssignmentService as FastAPI would."""
    admin_db_session_generator = admin_db_session()
    content_db_session_generator = content_db_session()

    admin_db: Session = next(admin_db_session_generator)
    content_db: Session = next(content_db_session_generator)

    try:
        content_cluster_engine = content_db_engine()
        content_db_cluster_svc = ContentDbClusterService(
            content_db=content_db,
            content_cluster_engine=content_cluster_engine,
        )
        courses_svc = CourseService(
            admin_db=admin_db, content_db_cluster_svc=content_db_cluster_svc
        )

        return AssignmentService(
            admin_db=admin_db,
            courses_svc=courses_svc,
            content_db_cluster_svc=content_db_cluster_svc,
        )
    finally:
        admin_db_session_generator.close()
        content_db_session_generator.close()
