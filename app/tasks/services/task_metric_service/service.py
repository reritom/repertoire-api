from typing import List

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.models.task_metric import TaskMetric
from app.tasks.schemas.task_metric_schema import TaskMetricCreationSchema

from ._service import (
    _create_task_metric,
    _delete_task_metric,
    _get_task_metric,
    _get_task_metrics,
)


def create_task_metric(
    session: SessionType,
    authenticated_user: User,
    task_metric_creation_payload: TaskMetricCreationSchema,
) -> TaskMetric:
    return _create_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_creation_payload=task_metric_creation_payload,
    )


def get_task_metric(
    session: SessionType,
    authenticated_user: User,
    task_metric_id: int,
) -> TaskMetric:
    return _get_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_id=task_metric_id,
    )


def get_task_metrics(
    session: SessionType,
    authenticated_user: User,
    task_id: int,
) -> List[TaskMetric]:
    return _get_task_metrics(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


def delete_task_metric(
    session: SessionType,
    authenticated_user: User,
    task_metric_id: int,
) -> None:
    return _delete_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_id=task_metric_id,
    )
