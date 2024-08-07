from datetime import datetime
from typing import List

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.daos.task_event_dao import TaskEventDao
from app.tasks.models.task_event import TaskEvent
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema
from app.tasks.services._dependencies import get_task_factory
from app.tasks.services.task_event_service._dependencies import (
    get_now_datetime,
    get_task_event_dao,
    get_task_id_from_task_event_creation_payload,
)

from ._utils import compute_effective_datetime
from .signals import task_event_created, task_event_deleted


@inject(
    extra_dependencies=[
        Depends(get_task_factory(get_task_id_from_task_event_creation_payload))
    ]
)
def _create_task_event(
    session: SessionType = Depends,
    authenticated_user: User = Depends,
    task_event_creation_payload: TaskEventCreationSchema = Depends,
    # Injected
    task_event_dao: TaskEventDao = Depends(get_task_event_dao),
    now: datetime = Depends(get_now_datetime),
) -> TaskEvent:
    task_event = task_event_dao.create(
        task_id=task_event_creation_payload.task_id,
        around=task_event_creation_payload.around,
        at=task_event_creation_payload.at,
        created=now,
        effective_datetime=compute_effective_datetime(
            task_event_creation_payload=task_event_creation_payload,
            created=now,
        ),
    )
    session.commit()
    task_event_created.send(
        session=session,
        task_id=task_event.task_id,
        authenticated_user=authenticated_user,
    )
    return task_event


@inject
def _delete_task_event(
    session: SessionType = Depends,
    authenticated_user: User = Depends,
    task_event_id: int = Depends,
    # Injected
    task_event_dao: TaskEventDao = Depends(get_task_event_dao),
) -> None:
    task_event = task_event_dao.get(id=task_event_id, user_id=authenticated_user.id)
    task_event_dao.delete(id=task_event_id, user_id=authenticated_user.id)
    session.commit()
    task_event_deleted.send(
        session=session,
        task_id=task_event.task_id,
        authenticated_user=authenticated_user,
    )


@inject
def _get_task_event(
    authenticated_user: User = Depends,
    task_event_id: int = Depends,
    # Injected
    task_event_dao: TaskEventDao = Depends(get_task_event_dao),
) -> TaskEvent:
    return task_event_dao.get(id=task_event_id, user_id=authenticated_user.id)


@inject
def _get_task_events(
    authenticated_user: User = Depends,
    task_id: int = Depends,
    # Injected
    task_event_dao: TaskEventDao = Depends(get_task_event_dao),
) -> List[TaskEvent]:
    return task_event_dao.list(task_id=task_id, user_id=authenticated_user.id)
