"""Models related to assignments"""

from pydantic import BaseModel


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

    assignment_id: int
    sql: str


class TestConfigurationSQLResponse(BaseModel):
    """Model that represents a response to testing the configuration SQL for an assignment."""

    success: bool
    error_message: str | None = None
    db_url: str | None = None


class SaveConfigurationSQLRequest(BaseModel):
    """Model that represents a request to save the configuration SQL for an assignment."""

    assignment_id: int
