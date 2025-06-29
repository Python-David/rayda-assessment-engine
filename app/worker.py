from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "integration_worker",
    broker=settings.REDIS_BROKER_URL,
    backend=settings.REDIS_BACKEND_URL
)

celery_app.conf.update(
    task_routes={
        "app.services.tasks.*": {"queue": "integration_queue"}
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

from app.services import tasks