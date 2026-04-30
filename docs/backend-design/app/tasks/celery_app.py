# ============================================
# SillyMD Backend - Celery App
# ============================================

from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "sillymd",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000
)


@celery_app.task
def test_task():
    """Test task"""
    return "Hello from Celery!"
