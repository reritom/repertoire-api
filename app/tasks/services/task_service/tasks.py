from app.celery import celery
from app.database import using_get_session

from . import service as task_service


@celery.task
def trigger_mark_ongoing_date_tasks_as_completed():
    with using_get_session() as session:
        task_service.mark_ongoing_date_tasks_as_completed(session=session)
