"""Contains the configuration for Celery allowing for a distributed task queue."""

from celery import Celery
from celery.schedules import crontab
from .env import env

celery_app = Celery(
    "app",
    broker=f"redis://{env.REDIS_PASSWORD}@{env.REDIS_HOST}:{env.REDIS_PORT}/0",
    backend=f"redis://{env.REDIS_PASSWORD}@{env.REDIS_HOST}:{env.REDIS_PORT}/1",
)

# Import /tasks to ensure they are registered with Celery
celery_app.autodiscover_tasks(["server.tasks.assignment"])
celery_app.autodiscover_tasks(["server.tasks.realtime"])

# Set up celery configuration
celery_app.conf.update(
    timezone="UTC",
    beat_schedule={
        "patch-student-db-triggers-every-5s": {
            "task": "realtime.update_tracking_databases",
            "schedule": 5.0,  # every 5 seconds
        }
    },
)

# Set up the celery worker
if __name__ == "__main__":
    celery_app.worker_main()
