"""Testing suite for the assignment service."""

import pytest
from jwt.exceptions import InvalidSignatureError

from ...entities import (
    UserAuthenticationProvider,
    UserEntity,
    CourseEntity,
    CourseMemberEntity,
    CourseMembershipRole,
    AssignmentState,
)
from ...models.assignment import CreateDraftRequest
from ...models.auth import Subject
from ...services import AssignmentService, ProjectAuthService
from ...services.project import auth_crypto as crypto
from ...env import env

# from ....entities import UserAuthenticationProvider
from .fixtures import assignment_svc


def test_create_draft_assignment(assignment_svc: AssignmentService):
    """Tests creating a draft assignment."""
    # TODO: Remove dependency to the _admin_db and properly seed test data
    user = UserEntity(
        id=1, auth_id="123456789", auth_provider=UserAuthenticationProvider.UNC_SSO
    )
    assignment_svc._admin_db.add(user)
    subject = Subject(id=1)
    course = CourseEntity(id=1)
    assignment_svc._admin_db.add(course)
    course_member = CourseMemberEntity(
        user_id=user.id, course_id=course.id, role=CourseMembershipRole.ADMIN
    )
    assignment_svc._admin_db.add(course_member)
    assignment_svc._admin_db.commit()

    # First, test that a draft assignment has been made correctly
    draft_request = CreateDraftRequest(
        name="Sample Assignment", course_id=course.id, is_group=False
    )
    draft_assignment = assignment_svc.create_draft(subject, draft_request)
    assert (
        draft_assignment.state == AssignmentState.DRAFT
    ), "Assignment should be created as a draft"
    # assert (
    #     draft_assignment.test_schema_view_role_name is not None
    # ), "View role name should be set"
    # assert (
    #     draft_assignment.encrypted_test_schema_admin_role_password is not None
    # ), "Role password should be set"

    # Then, test that a connection can be made to the project test schema using
    # the generated read-only role and password
    role_user = draft_assignment.test_db_view_role_name
    if draft_assignment.encrypted_test_db_view_role_password is not None:
        role_password = assignment_svc._content_db_cluster_svc.decrypt_role_password(
            draft_assignment.encrypted_test_db_view_role_password, draft_assignment.id
        )
    db_url = f"postgresql+psycopg2://{role_user}:{role_password}@{env.CONTENT_DB_HOST}:{env.CONTENT_DB_PORT}/{env.CONTENT_DB_DATABASE}_test"
    assert db_url is not None
