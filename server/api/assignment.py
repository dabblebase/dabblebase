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
    GetConfigurationSQLResponse,
    GetStaffViewResponse,
    GetStudentProjectsResponse,
    GetGroupProjectsResponse,
    CreateDraftRequest,
    CreateDraftResponse,
    RenameRequest,
    TestConfigurationSQLRequest,
    TestConfigurationSQLResponse,
    GetGroupsResponse,
    RenameGroupRequest,
    CreateGroupRequest,
    CreateGroupResponse,
    DeleteGroupRequest,
    AddGroupMemberRequest,
    RemoveGroupMemberRequest,
)
from ..models.task import Task
from ..tasks.assignment import publish_assignment as publish_assignment_task
from ..tasks.assignment import delete_assignment as delete_assignment_task

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


@api.get("/{assignment_id}/configuration-sql", tags=[tag])
def get_configuration_sql(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetConfigurationSQLResponse:
    """Get the configuration SQL for an assignment."""
    return assignment_svc.get_configuration_sql(subject, assignment_id)


@api.get("/{assignment_id}/staff-view", tags=[tag])
def get_staff_view(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetStaffViewResponse:
    """Get the staff view of an assignment."""
    return assignment_svc.get_staff_view(subject, assignment_id)


@api.get("/{assignment_id}/student-projects", tags=[tag])
def get_student_projects(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetStudentProjectsResponse:
    """Get the student projects for an assignment."""
    return assignment_svc.get_student_projects(subject, assignment_id)


@api.get("/{assignment_id}/group-projects", tags=[tag])
def get_group_projects(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetGroupProjectsResponse:
    """Get the student projects for an assignment."""
    return assignment_svc.get_group_projects(subject, assignment_id)


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


@api.put("/{assignment_id}/configuration-sql/test", tags=[tag])
def test_configuration_sql(
    assignment_id: int,
    request: TestConfigurationSQLRequest,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> TestConfigurationSQLResponse:
    """Test the configuration SQL for an assignment."""
    return assignment_svc.test_configuration_sql(subject, assignment_id, request)


@api.put("/{assignment_id}/configuration-sql/save", tags=[tag])
def save_configuration_sql(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Save the configuration SQL for an assignment."""
    return assignment_svc.save_configuration_sql(subject, assignment_id)


@api.put("/{assignment_id}/configuration-sql/remove", tags=[tag])
def remove_configuration_sql(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Reset the configuration SQL for an assignment."""
    return assignment_svc.remove_configuration_sql(subject, assignment_id)


@api.put("/{assignment_id}/configuration-sql/reset", tags=[tag])
def reset_configuration_sql(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Reset the configuration SQL for an assignment."""
    return assignment_svc.reset_configuration_sql(subject, assignment_id)


@api.get("/{assignment_id}/groups", tags=[tag])
def get_groups(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> GetGroupsResponse:
    """Get the groups of an assignment."""
    return assignment_svc.get_groups(subject, assignment_id)


@api.put("/{assignment_id}/group/{group_id}/rename", tags=[tag])
def rename_group(
    assignment_id: int,
    group_id: int,
    name: str,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Rename a group in an assignment."""
    request = RenameGroupRequest(group_id=group_id, name=name)
    return assignment_svc.rename_group(subject, request)


@api.post("/{assignment_id}/group", tags=[tag])
def create_group(
    assignment_id: int,
    request: CreateGroupRequest,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> CreateGroupResponse:
    """Create a new group in an assignment."""
    return assignment_svc.create_group(subject, assignment_id, request)


@api.delete("/{assignment_id}/group/{group_id}", tags=[tag])
def delete_group(
    assignment_id: int,
    group_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Delete a group in an assignment."""
    return assignment_svc.delete_group(subject, DeleteGroupRequest(group_id=group_id))


@api.post("/{assignment_id}/group/{group_id}/member", tags=[tag])
def add_group_member(
    assignment_id: int,
    request: AddGroupMemberRequest,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Add a member to a group in an assignment."""
    return assignment_svc.add_group_member(subject, request)


@api.delete("/{assignment_id}/group/{group_id}/member/{user_id}", tags=[tag])
def remove_group_member(
    assignment_id: int,
    group_id: int,
    user_id: int,
    subject: Subject = Depends(registered_user),
    assignment_svc: AssignmentService = Depends(),
) -> None:
    """Remove a member from a group in an assignment."""
    request = RemoveGroupMemberRequest(group_id=group_id, user_id=user_id)
    return assignment_svc.remove_group_member(subject, request)


@api.put("/{assignment_id}/publish", tags=[tag])
def publish_assignment(
    assignment_id: int,
    subject: Subject = Depends(registered_user),
) -> Task:
    """
    Publish an assignment.

    Note: This kicks off an asynchronous task using Celery and returns
    the task ID. The client can poll the task status endpoint to ensure
    the task has completed.
    """
    task = publish_assignment_task.delay(assignment_id, subject.id)
    return Task(task_id=task.id)


@api.delete("/{assignment_id}", tags=[tag])
def delete_assignment(
    assignment_id: int, subject: Subject = Depends(registered_user)
) -> Task:
    """Delete an assignment."""
    task = delete_assignment_task.delay(assignment_id, subject.id)
    return Task(task_id=task.id)
