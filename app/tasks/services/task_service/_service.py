from datetime import date
from typing import List, Optional

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.daos.task_dao import TaskDao
from app.tasks.daos.task_frequency_dao import TaskFrequencyDao
from app.tasks.daos.task_until_dao import TaskUntilDao
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_until import UntilType
from app.tasks.schemas.task_schema import TaskCreationSchema
from app.tasks.services._dependencies import get_task_dao
from app.tasks.services.task_service._dependencies import (
    get_date_now,
    get_task_frequency_dao,
    get_task_until_dao,
    validate_category_is_visible_for_task_creation,
    validate_name_is_unique_for_task_creation,
    validate_task_status_for_completion,
    validate_task_status_for_pause,
    validate_task_status_for_unpause,
)


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
    task_frequency_dao: TaskFrequencyDao = Depends(get_task_frequency_dao),
    task_until_dao: TaskUntilDao = Depends(get_task_until_dao),
) -> Task:
    until = task_until_dao.create(
        type=task_creation_payload.until.type,
        amount=task_creation_payload.until.amount,
        date=task_creation_payload.until.date,
    )
    frequency = task_frequency_dao.create(
        type=task_creation_payload.frequency.type,
        amount=task_creation_payload.frequency.amount,
        period=task_creation_payload.frequency.period,
        use_calendar_period=task_creation_payload.frequency.use_calendar_period,
        once_on_date=task_creation_payload.frequency.once_on_date,
        once_at_time=task_creation_payload.frequency.once_at_time,
        once_per_weekday=task_creation_payload.frequency.once_per_weekday,
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
    )
    session.commit()


@inject(extra_dependencies=[Depends(validate_task_status_for_unpause)])
def _unpause_task(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task_dao.update(
        id=task_id,
        user_id=authenticated_user.id,
        status=TaskStatus.ongoing,
    )
    session.commit()


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
    )
    session.commit()


@inject
def _recompute_task_status(
    session: SessionType = Depends,
    task_id: int = Depends,
    authenticated_user: User = Depends,
    # Injected
    now: date = Depends(get_date_now),
    task_dao: TaskDao = Depends(get_task_dao),
) -> None:
    task = task_dao.get(id=task_id)
    # TODO if an event is deleted, then a task could become incomplete
    print("In recompute")
    if task.manually_completed_at is not None:
        return

    if task.status == TaskStatus.completed:
        print(f"Is completed, {task.until.type} {len(task.events)} {task.until.amount}")
        if task.until.type == UntilType.amount and len(task.events) < task.until.amount:
            # An event was probably deleted, so this task is no longer complete
            task_dao.update(
                id=task_id,
                user_id=authenticated_user.id,
                status=TaskStatus.ongoing,
            )
            session.commit()

    elif task.status != TaskStatus.completed:
        if ((task.until.type == UntilType.date) and (now >= task.until.date)) or (
            (task.until.type == UntilType.amount)
            and (len(task.events) >= task.until.amount)
        ):
            task_dao.update(
                id=task_id,
                user_id=authenticated_user.id,
                status=TaskStatus.completed,
            )
            session.commit()
