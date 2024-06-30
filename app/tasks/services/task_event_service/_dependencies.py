from datetime import datetime

from app.database import SessionType
from app.tasks.daos.task_event_dao import TaskEventDao
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema


def get_task_event_dao(session: SessionType) -> TaskEventDao:
    return TaskEventDao(session=session)


def get_task_id_from_task_event_creation_payload(
    task_event_creation_payload: TaskEventCreationSchema,
) -> int:
    return task_event_creation_payload.task_id


def get_now_datetime() -> datetime:
    return datetime.utcnow()
