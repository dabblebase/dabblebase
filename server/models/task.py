"""Models related to celery tasks"""

from pydantic import BaseModel
from enum import Enum


class Task(BaseModel):
    """Represents a Celery asychronous task."""

    task_id: str


class TaskStatus(Enum):
    PENDING = "PENDING"
    RECEIVED = "RECEIVED"
    STARTED = "STARTED"
    SUCCESS = "SUCCESS"
    FAILURE = "FAILURE"
    RETRY = "RETRY"
    REVOKED = "REVOKED"
    IGNORED = "IGNORED"


class TaskStatusResponse(BaseModel):
    """Represents the status of a Celery task."""

    task_id: str
    status: TaskStatus
    result: str | None = None
    error: str | None = None
