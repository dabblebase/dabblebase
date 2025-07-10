"""Models related to courses"""

from pydantic import BaseModel
from datetime import datetime
from ..entities import CourseMembershipRole
from ..entities.course import CourseTermType


class GetDashboardResponse_Course(BaseModel):
    """Model that represents a course in the dashboard response."""

    id: int
    code: str
    name: str
    num_students: int | None = None
    num_assignments: int


class GetDashboardResponse(BaseModel):
    """Model that represents a response for the dashboard endpoint."""

    most_recent_staff_course_term: str | None
    most_recent_student_course_term: str | None
    other_staff_course_terms: list[str]
    other_student_course_terms: list[str]
    staff_courses: dict[str, list[GetDashboardResponse_Course]]
    student_courses: dict[str, list[GetDashboardResponse_Course]]


class GetDropdownResponse_Course(BaseModel):
    """Model that represents a course in the dropdown response."""

    id: int
    code: str
    name: str
    is_staff: bool


class GetDropdownRequest(BaseModel):
    """Model that represents a request for the dropdown endpoint."""

    search: str
    selected_course_id: int | None = None


class GetDropdownResponse(BaseModel):
    """Model that represents a dropdown response."""

    terms: list[str]
    selected_course: GetDropdownResponse_Course | None = None
    courses: dict[str, list[GetDropdownResponse_Course]]


class CreateCourseRequest(BaseModel):
    """Model that represents a request to create a course."""

    code: str
    name: str
    description: str | None = None
    term_type: CourseTermType
    term_year: int


class CreateCourseResponse(BaseModel):
    """Model that represents a response after creating a course."""

    id: int
    code: str
    name: str
    invite_code: str


class UpdateCourseRequest(BaseModel):
    """Model that represents a request to update a course."""

    id: int
    code: str
    name: str
    description: str | None = None
    term_type: CourseTermType
    term_year: int


class AddUserToCourseRequest(BaseModel):
    """Model that represents a request to add a user to a course."""

    course_id: int
    user_id: int


class JoinCourseRequest(BaseModel):
    """Model that represents a request to join a course."""

    invite_code: str


class JoinCourseResponse(BaseModel):
    """Model that represents a response after joining a course."""

    course_id: int
    course_code: str
    course_name: str


class ChangeUserRoleInCourseRequest(BaseModel):
    """Model that represents a request to change a user's role in a course."""

    course_id: int
    user_id: int
    role: CourseMembershipRole


class RemoveUserFromCourseRequest(BaseModel):
    """Model that represents a request to remove a user from a course."""

    course_id: int
    user_id: int
