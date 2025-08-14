"""Pydantic models for authentication"""

from pydantic import BaseModel


class Subject(BaseModel):
    """Represents a user making a request to the Dabblebase API"""

    id: int
