"""API endpoint for polling the status of asynchronous tasks."""

from fastapi import APIRouter, Depends

tag = "Tasks"
openapi_tags = {
    "name": tag,
    "description": "API endpoint for polling the status of asynchronous tasks.",
}

api = APIRouter(prefix="/api/task")
from celery.result import AsyncResult
from server.celery import celery_app
from ..models.task import TaskStatusResponse


@api.get("/{task_id}/status", tags=[tag])
def get_task_status(task_id: str) -> TaskStatusResponse:
    result = AsyncResult(task_id, app=celery_app)
    return TaskStatusResponse(
        task_id=task_id,
        status=result.status,
        result=result.result if result.successful() else None,
        error=str(result.result) if result.failed() else None,
    )
