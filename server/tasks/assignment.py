"""Celery tasks related to assignments."""

from ..celery import celery_app
from ..services import AssignmentService
from ..models.auth import Subject


@celery_app.task(name="assignment.publish")
def publish_assignment(
    assignment_svc: AssignmentService, subject: Subject, assignment_id: int
):
    """Celery task to publish an assignment."""
    assignment_svc.publish(subject, assignment_id)
