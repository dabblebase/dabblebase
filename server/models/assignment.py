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
