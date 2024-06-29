from typing import List

from fast_depends import Depends, inject

from app.accounts.models.user import User
from app.database import SessionType
from app.tasks.daos.task_metric_dao import TaskMetricDao
from app.tasks.models.task_metric import TaskMetric
from app.tasks.schemas.task_metric_schema import TaskMetricCreationSchema
from app.tasks.services._dependencies import get_task_factory
from app.tasks.services.task_metric_service._dependencies import (
    get_task_id_from_task_metric_creation_payload,
    get_task_metric_dao,
    validate_task_metric_name_from_task_metric_creation_payload,
)


@inject(
    extra_dependencies=[
        Depends(get_task_factory(get_task_id_from_task_metric_creation_payload)),
        Depends(validate_task_metric_name_from_task_metric_creation_payload),
    ]
)
def _create_task_metric(
    session: SessionType,
    task_metric_creation_payload: TaskMetricCreationSchema,
    # Injected
    task_metric_dao: TaskMetricDao = Depends(get_task_metric_dao),
) -> TaskMetric:
    task_metric = task_metric_dao.create(
        task_id=task_metric_creation_payload.task_id,
        name=task_metric_creation_payload.name,
        prompt=task_metric_creation_payload.prompt,
        required=task_metric_creation_payload.required,
    )
    session.commit()
    return task_metric


@inject
def _get_task_metric(
    authenticated_user: User,
    task_metric_id: int,
    # Injected
    task_metric_dao: TaskMetricDao = Depends(get_task_metric_dao),
) -> TaskMetric:
    return task_metric_dao.get(id=task_metric_id, user_id=authenticated_user.id)


@inject
def _get_task_metrics(
    authenticated_user: User,
    task_id: int,
    # Injected
    task_metric_dao: TaskMetricDao = Depends(get_task_metric_dao),
) -> List[TaskMetric]:
    return task_metric_dao.list(task_id=task_id, user_id=authenticated_user.id)


@inject
def _delete_task_metric(
    session: SessionType,
    authenticated_user: User,
    task_metric_id: int,
    # Injected
    task_metric_dao: TaskMetricDao = Depends(get_task_metric_dao),
) -> None:
    task_metric_dao.delete(id=task_metric_id, user_id=authenticated_user.id)
    session.commit()
