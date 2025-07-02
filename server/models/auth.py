"""Pydantic models for authentication"""

from pydantic import BaseModel


class Subject(BaseModel):
    """Represents a user making a request to the Tinkerbase API"""

    id: int
