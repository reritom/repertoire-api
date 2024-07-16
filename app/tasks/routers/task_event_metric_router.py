from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Depends, Path, Query

from app.accounts.models.user import User
from app.auth.routers.dependencies import (
    authenticated_user_required,
    get_authenticated_user,
)
from app.database import SessionType, get_session
from app.shared.tools import as_dict
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.schemas.task_event_metric_schema import (
    TaskEventMetricCreationSchema,
    TaskEventMetricSchema,
)
from app.tasks.services.task_event_metric_service import (
    service as task_event_metric_service,
)

router = APIRouter(
    tags=["Task event metrics"], dependencies=[Depends(authenticated_user_required)]
)


@router.post(
    "/task-event-metrics",
    response_model=TaskEventMetricSchema,
    status_code=201,
)
def create_task_event_metric(
    payload: TaskEventMetricCreationSchema,
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskEventMetric:
    return task_event_metric_service.create_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_creation_payload=payload,
    )


@dataclass
class TaskEventMetricFilters:
    task_event_id: Optional[int] = Query(None)
    task_metric_id: Optional[int] = Query(None)


@router.get(
    "/task-event-metrics",
    response_model=List[TaskEventMetricSchema],
    status_code=200,
)
def get_task_event_metrics(
    filters: TaskEventMetricFilters = Depends(TaskEventMetricFilters),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> List[TaskEventMetric]:
    return task_event_metric_service.get_task_event_metrics(
        session=session,
        authenticated_user=authenticated_user,
        **as_dict(filters),
    )


@router.get(
    "/task-event-metrics/{task_event_metric_id}",
    response_model=TaskEventMetricSchema,
    status_code=200,
)
def get_task_event_metric(
    task_event_metric_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskEventMetric:
    return task_event_metric_service.get_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_id=task_event_metric_id,
    )


@router.delete(
    "/task-event-metrics/{task_event_metric_id}",
    response_model=None,
    status_code=204,
)
def delete_task_event_metric(
    task_event_metric_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_event_metric_service.delete_task_event_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_event_metric_id=task_event_metric_id,
    )
