"""Models related to assignments"""

from pydantic import BaseModel


class CreateDraftRequest(BaseModel):
    """Model that represents a request to create a draft."""

    name: str
    course_id: int
    is_group: bool
    setup_sql: str
