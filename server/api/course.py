"""API endpoint for courses"""

import requests
from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException
from ..env import env
from ..services import CourseService
from ..entities import CourseMembershipRole
from datetime import datetime, timedelta, timezone
from ..services.project import auth_crypto as crypto
from ..api.auth import registered_user
from ..models.auth import Subject
from ..models.course import (
    GetDashboardResponse,
    GetDropdownRequest,
    GetDropdownResponse,
    GetAssignmentsResponse,
    GetRoleForCourseResponse,
)

tag = "Courses"
openapi_tags = {
    "name": tag,
    "description": "API endpoint for managing course-related data.",
}

api = APIRouter(prefix="/api/course")


@api.get("/dashboard", tags=[tag])
def get_dashboard(
    subject: Subject = Depends(registered_user), course_svc: CourseService = Depends()
) -> GetDashboardResponse:
    return course_svc.get_dashboard(subject)


@api.get("/dropdown", tags=[tag])
def get_dropdown(
    search: str = "",
    selected_course_id: int | None = None,
    subject: Subject = Depends(registered_user),
    course_svc: CourseService = Depends(),
) -> GetDropdownResponse:
    return course_svc.get_dropdown(
        subject,
        GetDropdownRequest(search=search, selected_course_id=selected_course_id),
    )


@api.get("/{course_id}/assignments", tags=[tag])
def get_assignments(
    course_id: int,
    subject: Subject = Depends(registered_user),
    course_svc: CourseService = Depends(),
) -> GetAssignmentsResponse:
    """
    Get assignments for a specific course.
    """
    return course_svc.get_assignments(subject, course_id)


@api.get("/{course_id}/role", tags=[tag])
def get_course_role(
    course_id: int,
    subject: Subject = Depends(registered_user),
    course_svc: CourseService = Depends(),
) -> GetRoleForCourseResponse:
    """
    Get the role of the user in the specified course.
    """
    return course_svc.get_role_for_course(subject, course_id)
