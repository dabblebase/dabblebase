"""Models related to projects"""

from pydantic import BaseModel


class CreateProjectRequest(BaseModel):
    """Model that represents a request to create a project."""

    assignment_id: int
    group_id: int | None = None
    user_id: int | None = None
