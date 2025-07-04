"""Models related to courses"""

from pydantic import BaseModel
from datetime import datetime
from ..entities import CourseMembershipRole


class CreateCourseRequest(BaseModel):
    """Model that represents a request to create a course."""

    code: str
    name: str
    description: str | None = None
    start_date: datetime
    end_date: datetime


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
    start_date: datetime
    end_date: datetime


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
