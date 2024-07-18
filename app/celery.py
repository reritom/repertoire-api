import logging

from celery import Celery
from celery.schedules import crontab

from app.settings import settings

logger = logging.getLogger(__name__)


celery = Celery(__name__, broker=settings.CELERY_BROKER_URL)


celery.conf.beat_schedule = {
    "trigger_mark_ongoing_date_tasks_as_completed__every_midnight": {
        "task": "app.tasks.services.task_service.tasks.trigger_mark_ongoing_date_tasks_as_completed",
        "schedule": crontab(),
    },
}
