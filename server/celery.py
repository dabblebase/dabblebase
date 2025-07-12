"""Contains the configuration for Celery allowing for a distributed task queue."""

from celery import Celery
from .env import env

celery_app = Celery(
    "app",
    broker=f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/0",
    backend=f"redis://{env.REDIS_HOST}:{env.REDIS_PORT}/1",
)

# Import /tasks to ensure they are registered with Celery
celery_app.autodiscover_tasks(["server.tasks.assignment"])

# Set up the celery worker
if __name__ == "__main__":
    celery_app.worker_main()
