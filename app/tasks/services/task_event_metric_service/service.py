from typing import List

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.schemas.task_event_metric_schema import TaskEventMetricCreationSchema

from ._service import (
    _create_task_event_metric,
    _delete_task_event_metric,
    _get_task_event_metric,
    _get_task_event_metrics,
)


def create_task_event_metric(
    session: SessionType,
    authenticated_user: User,
    task_event_metric_creation_payload: TaskEventMetricCreationSchema,
) -> TaskEventMetric:
    return _create_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_creation_payload=task_event_metric_creation_payload,
    )


def get_task_event_metric(
    session: SessionType,
    authenticated_user: User,
    task_event_metric_id: int,
) -> TaskEventMetric:
    return _get_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_id=task_event_metric_id,
    )


def get_task_event_metrics(
    session: SessionType,
    authenticated_user: User,
    task_event_id: OptionalFilter[int] = NO_FILTER,
    task_metric_id: OptionalFilter[int] = NO_FILTER,
) -> List[TaskEventMetric]:
    return _get_task_event_metrics(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_id,
        task_metric_id=task_metric_id,
    )


def delete_task_event_metric(
    session: SessionType,
    authenticated_user: User,
    task_event_metric_id: int,
) -> None:
    return _delete_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_id=task_event_metric_id,
    )
