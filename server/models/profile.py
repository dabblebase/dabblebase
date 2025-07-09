"""Models related to profiles"""

from pydantic import BaseModel


class GetProfileSummaryResponse(BaseModel):
    """Model that represents a response for the profile endpoint."""

    first_name: str
    last_name: str
    email: str
    initials: str
