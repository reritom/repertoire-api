from typing import List, Optional

from anyio.abc._tasks import TaskStatus

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task import Task
from app.tasks.schemas.task_schema import (
    TaskCreationSchema,
    TaskFrequencyCreationSchema,
    TaskUntilCreationSchema,
)

from ._service import (
    _complete_task,
    _create_task,
    _delete_task,
    _get_task,
    _get_tasks,
    _mark_ongoing_date_tasks_as_completed,
    _pause_task,
    _recompute_task_state,
    _unpause_task,
    _update_task_frequency,
    _update_task_until,
)


def create_task(
    session: SessionType,
    authenticated_user: User,
    task_creation_payload: TaskCreationSchema,
) -> Task:
    return _create_task(
        session=session,
        authenticated_user=authenticated_user,
        task_creation_payload=task_creation_payload,
    )


def get_task(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> Task:
    return _get_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def get_tasks(
    session: SessionType,
    authenticated_user: User,
    status: OptionalFilter[TaskStatus] = NO_FILTER,
    category_id: OptionalFilter[Optional[int]] = NO_FILTER,
) -> List[Task]:
    return _get_tasks(
        session=session,
        authenticated_user=authenticated_user,
        status=status,
        category_id=category_id,
    )


def delete_task(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> None:
    return _delete_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def pause_task(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> None:
    return _pause_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def unpause_task(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> None:
    return _unpause_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def complete_task(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> None:
    return _complete_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def recompute_task_state(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> None:
    return _recompute_task_state(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
    )


def update_task_frequency(
    session: SessionType,
    task_id: int,
    authenticated_user: User,
    frequency_creation_payload: TaskFrequencyCreationSchema,
) -> None:
    return _update_task_frequency(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
        frequency_creation_payload=frequency_creation_payload,
    )


def update_task_until(
    session: SessionType,
    task_id: int,
    authenticated_user: User,
    until_creation_payload: TaskUntilCreationSchema,
) -> None:
    return _update_task_until(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
        until_creation_payload=until_creation_payload,
    )


def mark_ongoing_date_tasks_as_completed(session: SessionType):
    # TODO test
    _mark_ongoing_date_tasks_as_completed(session=session)
