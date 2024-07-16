from typing import List

from fastapi import APIRouter, Depends, Path, Query

from app.accounts.models.user import User
from app.auth.routers.dependencies import (
    authenticated_user_required,
    get_authenticated_user,
)
from app.database import SessionType, get_session
from app.tasks.models.task_metric import TaskMetric
from app.tasks.schemas.task_metric_schema import (
    TaskMetricCreationSchema,
    TaskMetricSchema,
)
from app.tasks.services.task_metric_service import service as task_metric_service

router = APIRouter(
    tags=["Task metrics"], dependencies=[Depends(authenticated_user_required)]
)


@router.post(
    "/task-metrics",
    response_model=TaskMetricSchema,
    status_code=201,
)
def create_task_metric(
    payload: TaskMetricCreationSchema,
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskMetric:
    return task_metric_service.create_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_creation_payload=payload,
    )


@router.get(
    "/task-metrics",
    response_model=List[TaskMetricSchema],
    status_code=200,
)
def get_task_metrics(
    task_id: int = Query(...),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> List[TaskMetric]:
    return task_metric_service.get_task_metrics(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.get(
    "/task-metrics/{task_metric_id}",
    response_model=TaskMetricSchema,
    status_code=200,
)
def get_task_metric(
    task_metric_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskMetric:
    return task_metric_service.get_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_id=task_metric_id,
    )


@router.delete(
    "/task-metrics/{task_metric_id}",
    response_model=None,
    status_code=204,
)
def delete_task_metric(
    task_metric_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_metric_service.delete_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_id=task_metric_id,
    )
