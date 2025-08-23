"""Testing suite for the profile service."""

import pytest
from ....entities import UserEntity
from ....models.profile import *
from ....models.auth import Subject
from ....services import ProfileService
from ..fixtures import profile_svc
from ....seeds.demo import (
    seed_demo_fixture,
    instructor_user,
    admin_user,
    ta_user,
    student_1_user,
    course,
    nocourse_student_user,
)
from ....services.exceptions import (
    InputValidationException,
    UserPermissionException,
    ResourceNotFoundException,
    ResourceAlreadyExistsException,
)
from sqlalchemy.orm import Session


def test_get_summary(profile_svc: ProfileService):
    """Test getting a profile summary."""
    user = profile_svc.get_profile_summary(instructor_user.to_subject())
    assert user.first_name == instructor_user.first_name
    assert user.last_name == instructor_user.last_name
    assert user.email == instructor_user.email
    assert (
        user.initials
        == instructor_user.first_name[0].upper() + instructor_user.last_name[0].upper()
    )


def test_get_summary_not_found(profile_svc: ProfileService):
    """Ensure that an exception is raised when a profile is not found."""
    with pytest.raises(ResourceNotFoundException):
        profile_svc.get_profile_summary(Subject(id=404))
