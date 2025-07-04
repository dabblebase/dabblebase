"""Testing suite for the courses service."""

from ...models.course import *
from ...services import CourseService
from .fixtures import course_svc
from .seed import seed_database, instructor_user
from datetime import datetime, timedelta


def test_create_course(course_svc: CourseService):
    """Tests creating a course."""

    # Create a course
    request = CreateCourseRequest(
        code="TEST123",
        name="Test Course",
        description="This is a test course.",
        start_date=datetime.now() - timedelta(days=30),
        end_date=datetime.now() + timedelta(days=30),
    )
    course = course_svc.create_course(instructor_user.to_subject(), request)

    # Verify that the course was created successfully
    assert course is not None, "Course creation should return a course object"
    assert course.id is not None, "Course should have an ID after creation"
    assert course.name == "Test Course", "Course name should match the input"
    assert (
        course.invite_code is not None
    ), "Course should have an invite code after creation"
