"""Models related to admin actions"""

from pydantic import BaseModel


class ListUsersResponse_User(BaseModel):
    """Model that represents a user for the list users endpoint"""

    id: int
    name: str
    email: str
    is_instructor: bool


class ListUsersResponse(BaseModel):
    """Model that represents a response for the list users endpoint"""

    users: list[ListUsersResponse_User]
