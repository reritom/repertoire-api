from typing import List

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.models.task_event import TaskEvent
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema

from ._service import (
    _create_task_event,
    _delete_task_event,
    _get_task_event,
    _get_task_events,
)


def create_task_event(
    session: SessionType,
    authenticated_user: User,
    task_event_creation_payload: TaskEventCreationSchema,
) -> TaskEvent:
    return _create_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_creation_payload=task_event_creation_payload,
    )


def delete_task_event(
    session: SessionType,
    authenticated_user: User,
    task_event_id: int,
) -> None:
    return _delete_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_id,
    )


def get_task_event(
    session: SessionType,
    authenticated_user: User,
    task_event_id: int,
) -> TaskEvent:
    return _get_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_id,
    )


def get_task_events(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> List[TaskEvent]:
    return _get_task_events(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )
