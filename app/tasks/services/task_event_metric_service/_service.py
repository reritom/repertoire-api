from typing import List

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.daos.task_event_metric_dao import TaskEventMetricDao
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.schemas.task_event_metric_schema import TaskEventMetricCreationSchema
from app.tasks.services.task_event_metric_service._dependencies import (
    get_task_event_from_task_event_metric_creation_payload,
    get_task_event_metric_dao,
    get_task_metric_from_task_event_metric_creation_payload,
    validate_task_event_metric_unique_in_task_event_metric_creation_payload,
    validate_task_metric_and_task_event_are_same_task_in_task_event_metric_creation_payload,
)


@inject(
    extra_dependencies=[
        Depends(get_task_metric_from_task_event_metric_creation_payload),
        Depends(get_task_event_from_task_event_metric_creation_payload),
        Depends(
            validate_task_metric_and_task_event_are_same_task_in_task_event_metric_creation_payload
        ),
        Depends(
            validate_task_event_metric_unique_in_task_event_metric_creation_payload
        ),
    ]
)
def _create_task_event_metric(
    session: SessionType,
    task_event_metric_creation_payload: TaskEventMetricCreationSchema,
    # Injected
    task_event_metric_dao: TaskEventMetricDao = Depends(get_task_event_metric_dao),
) -> TaskEventMetric:
    # TODO maybe consider max number of task event metrics for a given task metric?
    task_event_metric = task_event_metric_dao.create(
        task_metric_id=task_event_metric_creation_payload.task_metric_id,
        task_event_id=task_event_metric_creation_payload.task_event_id,
        value=task_event_metric_creation_payload.value,
    )
    session.commit()
    return task_event_metric


@inject
def _get_task_event_metric(
    authenticated_user: User,
    task_event_metric_id: int,
    # Injected
    task_event_metric_dao: TaskEventMetricDao = Depends(get_task_event_metric_dao),
) -> TaskEventMetric:
    return task_event_metric_dao.get(
        user_id=authenticated_user.id,
        id=task_event_metric_id,
    )


@inject
def _get_task_event_metrics(
    authenticated_user: User,
    task_event_id: OptionalFilter[int] = NO_FILTER,
    task_metric_id: OptionalFilter[int] = NO_FILTER,
    # Injected
    task_event_metric_dao: TaskEventMetricDao = Depends(get_task_event_metric_dao),
) -> List[TaskEventMetric]:
    return task_event_metric_dao.list(
        user_id=authenticated_user.id,
        task_event_id=task_event_id,
        task_metric_id=task_metric_id,
    )


@inject
def _delete_task_event_metric(
    session: SessionType,
    authenticated_user: User,
    task_event_metric_id: int,
    # Injected
    task_event_metric_dao: TaskEventMetricDao = Depends(get_task_event_metric_dao),
) -> None:
    task_event_metric_dao.delete(
        id=task_event_metric_id,
        user_id=authenticated_user.id,
    )
    session.commit()
