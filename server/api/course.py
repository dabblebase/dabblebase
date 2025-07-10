"""API endpoint for courses"""

import requests
from fastapi import APIRouter, Depends
from fastapi.responses import Response, RedirectResponse
from fastapi.exceptions import HTTPException
from ..env import env
from ..services import CourseService
from ..entities import UserAuthenticationProvider
from datetime import datetime, timedelta, timezone
from ..services.project import auth_crypto as crypto
from ..api.auth import registered_user
from ..models.auth import Subject
from ..models.course import (
    GetDashboardResponse,
    GetDropdownRequest,
    GetDropdownResponse,
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
