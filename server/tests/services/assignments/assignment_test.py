"""Testing suite for the assignments service."""

import pytest
from ....entities import AssignmentEntity
from ....models.course import *
from ....services import AssignmentService
from ..fixtures import course_svc
from ..seed import (
    seed_database,
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    course,
    nocourse_student_user,
)

from .assignment_data import create_draft_request
from ....services.exceptions import (
    InputValidationException,
    UserPermissionException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)
from datetime import datetime, timedelta
from sqlalchemy.orm import Session


def test_create_draft(admin_db_session: Session, assignment_svc: AssignmentService):
    """Tests creating a draft assignment."""
    assignment_svc.create_draft(instructor_user.to_subject(), create_draft_request)
