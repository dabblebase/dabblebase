"""API endpoint for assignments"""

from fastapi import APIRouter, Depends
from ..env import env
from ..services import AssignmentService
from ..services.project import auth_crypto as crypto
from ..api.auth import registered_user
from ..models.auth import Subject
from ..models.assignment import (
    GetDropdownRequest,
    GetDropdownResponse,
    GetViewResponse,
    GetDraftResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    RenameRequest,
)

tag = "Assignments"
openapi_tags = {
    "name": tag,
    "description": "API endpoint for managing assignment-related data.",
}

api = APIRouter(prefix="/api/assignment")


@api.get("/dropdown", tags=[tag])
def get_dropdown(
    course_id: int,
    search: str = "",
    selected_assignment_id: int | None = None,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetDropdownResponse:
    request = GetDropdownRequest(
        search=search,
        course_id=course_id,
        selected_assignment_id=selected_assignment_id,
    )
    return assignment_svc.get_dropdown(subject, request)


@api.get("/{assignment_id}/view", tags=[tag])
def get_view(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetViewResponse:
    return assignment_svc.get_view(subject, assignment_id)


@api.get("/{assignment_id}/draft", tags=[tag])
def get_draft(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetDraftResponse:
    return assignment_svc.get_draft(subject, assignment_id)


@api.post("/draft", tags=[tag])
def create_draft(
    request: CreateDraftRequest,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> CreateDraftResponse:
    return assignment_svc.create_draft(subject, request)


@api.put("/{assignment_id}/rename", tags=[tag])
def rename(
    assignment_id: int,
    name: str,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Rename an existing assignment."""
    request = RenameRequest(assignment_id=assignment_id, name=name)
    return assignment_svc.rename(subject, request)
