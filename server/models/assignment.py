"""Models related to assignments"""

from pydantic import BaseModel
from ..entities import AssignmentState, CourseMembershipRole


class GetDropdownRequest(BaseModel):
    """Model that represents a request for the dropdown endpoint."""

    search: str
    course_id: int
    selected_assignment_id: int | None = None


class GetDropdownResponse_Assignment(BaseModel):
    """Model that represents an assignment in the dropdown response."""

    id: int
    name: str
    state: AssignmentState


class GetDropdownResponse(BaseModel):
    """Model that represents a response for the dropdown endpoint."""

    is_staff: bool
    selected_assignment: GetDropdownResponse_Assignment | None = None
    assignments: list[GetDropdownResponse_Assignment]


class GetViewResponse(BaseModel):
    """Model that represents a response for viewing an assignment."""

    role: CourseMembershipRole
    assignment_state: AssignmentState
    should_redirect: bool = False


class GetDraftResponse(BaseModel):
    """Model that represents a response for getting a draft assignment."""

    assignment_id: int
    name: str
    is_group: bool


class GetConfigurationSQLResponse(BaseModel):
    """Model that represents a response for getting the configuration SQL of an assignment."""

    sql: str | None = None
    sql_draft: str | None = None
    sql_draft_success: bool | None = None
    sql_draft_error: str | None = None
    db_url: str | None = None


class GetStaffViewResponse(BaseModel):
    """Model that presents the information for a staff view of an assignment."""

    assignment_id: int
    name: str
    is_group: bool
    state: AssignmentState
    configuration_sql: str | None = None


class GetStudentProjectsResponse_Project(BaseModel):
    """Model that represents a project in the response for getting student projects."""

    project_id: int
    user_id: int
    user_name: str
    user_email: str
    db_url: str


class GetStudentProjectsResponse(BaseModel):
    """Model that represents a response for getting student projects of an assignment."""

    projects: list[GetStudentProjectsResponse_Project]


class GetGroupProjectsResponse_Project(BaseModel):
    """Model that represents a group in the response for getting group projects of an assignment."""

    project_id: int
    group_id: int
    group_name: str
    group_members: list[str]
    group_member_emails: list[str]
    db_url: str


class GetGroupProjectsResponse(BaseModel):
    """Model that represents a response for getting group projects of an assignment."""

    projects: list[GetGroupProjectsResponse_Project]


class GetStudentDatabase(BaseModel):
    """Model that represents a response for getting the database URL of a student project."""

    db_url: str


class GetStudentAuth(BaseModel):
    """Model that represents a response for getting the authentication details of a student project."""

    auth_public_key: str


class GetStudentRealtime(BaseModel):
    """Model that represents a response for getting the realtime details of a student project."""

    realtime_token: str


class CreateDraftRequest(BaseModel):
    """Model that represents a request to create a draft."""

    name: str
    course_id: int
    is_group: bool


class CreateDraftResponse(BaseModel):
    """Model that represents a response to creating a draft."""

    assignment_id: int


class RenameRequest(BaseModel):
    """Model that represents a request to rename an assignment."""

    assignment_id: int
    name: str


class TestConfigurationSQLRequest(BaseModel):
    """Model that represents a request to test the configuration SQL for an assignment."""

    sql: str


class TestConfigurationSQLResponse(BaseModel):
    """Model that represents a response to testing the configuration SQL for an assignment."""

    success: bool
    error_message: str | None = None
    db_url: str | None = None


class GetGroupsResponse_User(BaseModel):
    """Model that represents a member of a group in the response for getting groups of an assignment."""

    user_id: int
    user_name: str


class GetGroupsResponse_Group(BaseModel):
    """Model that represents a group in the response for getting groups of an assignment."""

    group_id: int
    group_name: str
    members: list[GetGroupsResponse_User]


class GetGroupsResponse(BaseModel):
    """Model that represents a response for getting groups of an assignment."""

    groups: list[GetGroupsResponse_Group]
    unassigned_students: list[GetGroupsResponse_User]


class CreateGroupRequest(BaseModel):
    """Model that represents a request to create a group for an assignment."""

    group_name: str


class CreateGroupResponse(BaseModel):
    """Model that represents a response to creating a group for an assignment."""

    group_id: int
    group_name: str


class RenameGroupRequest(BaseModel):
    """Model that represents a request to rename a group."""

    group_id: int
    name: str


class AddGroupMemberRequest(BaseModel):
    """Model that represents a request to add a member to a group for an assignment."""

    group_id: int
    user_id: int


class RemoveGroupMemberRequest(BaseModel):
    """Model that represents a request to remove a member from a group for an assignment."""

    group_id: int
    user_id: int


class DeleteGroupRequest(BaseModel):
    """Model that represents a request to delete a group for an assignment."""

    group_id: int
