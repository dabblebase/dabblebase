"""Testing suite for the assignments service."""

import pytest
from ....env import env
from ....entities import AssignmentEntity, AssignmentState
from ....models.course import *
from ....services import AssignmentService
from ..fixtures import assignment_svc
from ..seed import (
    seed_database,
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    course,
    nocourse_student_user,
)

from .assignment_data import (
    create_draft_request,
    rename_request,
    rename_request_name_empty,
    rename_request_not_found,
)
from ....services.exceptions import (
    InputValidationException,
    UserPermissionException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text


def test_create_draft(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests creating a draft assignment."""
    # Test the creation of the assignment object
    response = assignment_svc.create_draft(
        instructor_user.to_subject(), create_draft_request
    )
    draft_assignment: AssignmentEntity | None = admin_db_session.query(
        AssignmentEntity
    ).get(response.assignment_id)
    assert draft_assignment is not None
    assert draft_assignment.state == AssignmentState.DRAFT
    assert draft_assignment.test_db_name is not None
    assert draft_assignment.test_db_admin_role_name is not None
    assert draft_assignment.encrypted_test_db_admin_role_password is not None
    assert draft_assignment.test_db_view_role_name is not None
    assert draft_assignment.encrypted_test_db_view_role_password is not None

    # Attempt to connect to the admin database using the admin role
    admin_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        draft_assignment.encrypted_test_db_admin_role_password, draft_assignment.id
    )
    db_url = f"postgresql+psycopg2://{draft_assignment.test_db_admin_role_name}:{admin_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{draft_assignment.test_db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1

    # Attempt to connect to the admin database using the view role
    view_role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
        draft_assignment.encrypted_test_db_view_role_password, draft_assignment.id
    )
    db_url = f"postgresql+psycopg2://{draft_assignment.test_db_view_role_name}:{view_role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{draft_assignment.test_db_name}"
    engine = create_engine(db_url, echo=True)
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        assert result.scalar() == 1


def test_create_draft_no_permissions(assignment_svc: AssignmentService):
    """Ensures that a user without permissions cannot create a draft assignment."""
    with pytest.raises(UserPermissionException):
        assignment_svc.create_draft(ta_user.to_subject(), create_draft_request)
    with pytest.raises(UserPermissionException):
        assignment_svc.create_draft(student_1_user.to_subject(), create_draft_request)


def test_rename(admin_db_session: Session, assignment_svc: AssignmentService):
    """Ensures that an assignment can be renamed."""
    assignment_svc.rename(instructor_user.to_subject(), rename_request)
    renamed_assignment = admin_db_session.query(AssignmentEntity).get(
        rename_request.assignment_id
    )
    assert renamed_assignment is not None
    assert renamed_assignment.name == rename_request.name


def test_rename_no_permissions(assignment_svc: AssignmentService):
    """Ensures that a user without permissions cannot rename an assignment."""
    with pytest.raises(UserPermissionException):
        assignment_svc.rename(ta_user.to_subject(), rename_request)
    with pytest.raises(UserPermissionException):
        assignment_svc.rename(student_1_user.to_subject(), rename_request)


def test_rename_name_empty(assignment_svc: AssignmentService):
    """Ensures that renaming an assignment to an empty name raises an exception."""
    with pytest.raises(InputValidationException):
        assignment_svc.rename(instructor_user.to_subject(), rename_request_name_empty)


def test_rename_not_found(assignment_svc: AssignmentService):
    """Ensures that renaming a non-existent assignment raises an exception."""
    with pytest.raises(ResourceNotFoundException):
        assignment_svc.rename(instructor_user.to_subject(), rename_request_not_found)
