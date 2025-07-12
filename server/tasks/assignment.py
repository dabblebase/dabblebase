"""Celery tasks related to assignments."""

from fastapi import Depends
from ..celery import celery_app
from ..services import AssignmentService
from ..models.auth import Subject
from .di_generators import get_assignment_service


@celery_app.task(name="assignment.publish")
def publish_assignment(assignment_id: int, user_id: int):
    """Celery task to publish an assignment."""
    subject = Subject(id=user_id)
    assignment_svc = get_assignment_service()
    assignment_svc.publish(subject, assignment_id)


@celery_app.task(name="assignment.delete")
def delete_assignment(assignment_id: int, user_id: int):
    """Celery task to delete an assignment."""
    subject = Subject(id=user_id)
    assignment_svc = get_assignment_service()
    assignment_svc.delete(subject, assignment_id)
