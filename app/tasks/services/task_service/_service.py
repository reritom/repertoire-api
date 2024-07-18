from datetime import date, datetime
from typing import List, Optional

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.daos.task_dao import TaskDao
from app.tasks.daos.task_frequency_dao import TaskFrequencyDao
from app.tasks.daos.task_until_dao import TaskUntilDao
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_frequency import TaskFrequency
from app.tasks.models.task_until import TaskUntil
from app.tasks.schemas.task_schema import (
    TaskCreationSchema,
    TaskFrequencyCreationSchema,
    TaskUntilCreationSchema,
)
from app.tasks.services._dependencies import get_task as get_task_dependency
from app.tasks.services._dependencies import get_task_dao
from app.tasks.services.task_service._dependencies import (
    get_date_now,
    get_datetime_now,
    get_task_frequency_dao,
    get_task_until_dao,
    validate_category_is_visible_for_task_creation,
    validate_name_is_unique_for_task_creation,
    validate_task_status_for_completion,
    validate_task_status_for_pause,
    validate_task_status_for_unpause,
)
from app.tasks.services.task_service._utils import (
    compute_task_state,
)
from app.tasks.services.task_service.signals import task_updated


@inject(
    extra_dependencies=[
        Depends(validate_name_is_unique_for_task_creation),
        Depends(validate_category_is_visible_for_task_creation),
    ]
)
def _create_task(
    session: SessionType,
    authenticated_user: User,
    task_creation_payload: TaskCreationSchema,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> Task:
    until = _create_until(
        session=session,
        until_creation_payload=task_creation_payload.until,
    )
    frequency = _create_frequency(
        frequency_creation_payload=task_creation_payload.frequency,
        session=session,
    )
    task = task_dao.create(
        name=task_creation_payload.name,
        description=task_creation_payload.description,
        category_id=task_creation_payload.category_id,
        frequency_id=frequency.id,
        until_id=until.id,
        user_id=authenticated_user.id,
    )
    session.commit()
    task_updated.send(
        session=session,
        task_id=task.id,
        authenticated_user=authenticated_user,
    )
    session.refresh(task)
    return task


@inject
def _get_task(
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> Task:
    return task_dao.get(user_id=authenticated_user.id, id=task_id)


@inject
def _get_tasks(
    authenticated_user: User = Depends,
    status: OptionalFilter[TaskStatus] = NO_FILTER,
    category_id: OptionalFilter[Optional[int]] = NO_FILTER,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> List[Task]:
    return task_dao.list(
        user_id=authenticated_user.id,
        status=status,
        category_id=category_id,
    )


@inject
def _delete_task(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task_dao.delete(
        id=task_id,
        user_id=authenticated_user.id,
    )
    session.commit()


@inject(extra_dependencies=[Depends(validate_task_status_for_pause)])
def _pause_task(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        status=TaskStatus.paused,
        next_event_datetime=None,
    )
    session.commit()


@inject(extra_dependencies=[Depends(validate_task_status_for_unpause)])
def _unpause_task(
    session: SessionType = Depends,
    authenticated_user: User = Depends,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
    task: Task = Depends(get_task_dependency),
) -> None:
    task_dao.update(
        id=task.id,
        user_id=authenticated_user.id,
        status=TaskStatus.ongoing,
    )
    session.commit()
    task_updated.send(
        session=session,
        task_id=task.id,
        authenticated_user=authenticated_user,
    )


@inject(extra_dependencies=[Depends(validate_task_status_for_completion)])
def _complete_task(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    now: date = Depends(get_date_now),
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        status=TaskStatus.completed,
        manually_completed_at=now,
        next_event_datetime=None,
    )
    session.commit()


@inject
def _recompute_task_state(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    now: datetime = Depends(get_datetime_now),
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task = task_dao.get(id=task_id)
    status, next_event_datetime = compute_task_state(task=task, now=now)
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        status=status,
        next_event_datetime=next_event_datetime,
    )
    session.commit()


@inject
def _create_frequency(
    frequency_creation_payload: TaskFrequencyCreationSchema = Depends,
    # Injected
    task_frequency_dao: TaskFrequencyDao = Depends(get_task_frequency_dao),
) -> TaskFrequency:
    # Create an uncommitted, unlinked task frequency
    return task_frequency_dao.create(
        type=frequency_creation_payload.type,
        amount=frequency_creation_payload.amount,
        period=frequency_creation_payload.period,
        use_calendar_period=frequency_creation_payload.use_calendar_period,
        once_on_date=frequency_creation_payload.once_on_date,
        once_at_time=frequency_creation_payload.once_at_time,
        once_per_weekday=frequency_creation_payload.once_per_weekday,
    )


@inject
def _create_until(
    until_creation_payload: TaskUntilCreationSchema = Depends,
    # Injected
    task_until_dao: TaskUntilDao = Depends(get_task_until_dao),
) -> TaskUntil:
    # Create an uncommitted, unlinked task until
    return task_until_dao.create(
        type=until_creation_payload.type,
        amount=until_creation_payload.amount,
        date=until_creation_payload.date,
    )


@inject
def _update_task_frequency(
    session: SessionType,
    task_id: int,
    authenticated_user: User,
    frequency_creation_payload: TaskFrequencyCreationSchema,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
    task_frequency_dao: TaskFrequencyDao = Depends(get_task_frequency_dao),
    task: Task = Depends(get_task_dependency),
) -> None:
    frequency = _create_frequency(
        session=session,
        frequency_creation_payload=frequency_creation_payload,
    )
    old_frequency_id = task.frequency_id
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        frequency_id=frequency.id,
    )
    session.commit()
    task_frequency_dao.delete(
        id=old_frequency_id,
    )
    session.commit()
    task_updated.send(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
    )


@inject
def _update_task_until(
    session: SessionType,
    task_id: int,
    authenticated_user: User,
    until_creation_payload: TaskUntilCreationSchema,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
    task_until_dao: TaskUntilDao = Depends(get_task_until_dao),
    task: Task = Depends(get_task_dependency),
) -> None:
    until = _create_until(
        until_creation_payload=until_creation_payload,
        session=session,
    )
    old_until_id = task.until_id
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        until_id=until.id,
    )
    session.commit()
    task_until_dao.delete(
        id=old_until_id,
    )
    session.commit()
    task_updated.send(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
    )


@inject
def _mark_ongoing_date_tasks_as_completed(
    session: SessionType,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
):
    task_dao.mark_ongoing_date_tasks_as_completed()
    session.commit()
