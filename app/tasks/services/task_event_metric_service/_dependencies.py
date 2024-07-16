from fast_depends import Depends

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.exceptions import ServiceValidationError
from app.tasks.daos.task_event_metric_dao import TaskEventMetricDao
from app.tasks.models.task_event import TaskEvent
from app.tasks.models.task_metric import TaskMetric
from app.tasks.schemas.task_event_metric_schema import TaskEventMetricCreationSchema
from app.tasks.services.task_event_service.service import get_task_event
from app.tasks.services.task_metric_service.service import get_task_metric


def get_task_event_metric_dao(session: SessionType) -> TaskEventMetricDao:
    return TaskEventMetricDao(session=session)


def get_task_metric_from_task_event_metric_creation_payload(
    task_event_metric_creation_payload: TaskEventMetricCreationSchema = Depends,
    session: SessionType = Depends,
    authenticated_user: User = Depends,
) -> TaskMetric:
    # A NoResultFound will be raised if the user can't use this task metric
    # TODO reraise service validation error
    return get_task_metric(
        session=session,
        authenticated_user=authenticated_user,
        task_metric_id=task_event_metric_creation_payload.task_metric_id,
    )


def get_task_event_from_task_event_metric_creation_payload(
    task_event_metric_creation_payload: TaskEventMetricCreationSchema = Depends,
    session: SessionType = Depends,
    authenticated_user: User = Depends,
) -> TaskEvent:
    # A NoResultFound will be raised if the user can't use this task event
    # TODO reraise service validation error
    return get_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_metric_creation_payload.task_event_id,
    )


def validate_task_event_metric_unique_in_task_event_metric_creation_payload(
    task_event_metric_creation_payload: TaskEventMetricCreationSchema = Depends,
    task_event_metric_dao: TaskEventMetricDao = Depends(get_task_event_metric_dao),
):
    if task_event_metric_dao.get(
        task_event_id=task_event_metric_creation_payload.task_event_id,
        task_metric_id=task_event_metric_creation_payload.task_metric_id,
        raise_exc=False,
    ):
        raise ServiceValidationError("A metric value has already been applied")


def validate_task_metric_and_task_event_are_same_task_in_task_event_metric_creation_payload(
    task_event: TaskEvent = Depends(
        get_task_event_from_task_event_metric_creation_payload
    ),
    task_metric: TaskMetric = Depends(
        get_task_metric_from_task_event_metric_creation_payload
    ),
):
    if task_event.task_id != task_metric.task_id:
        raise ServiceValidationError(
            "Task metric and event aren't related to the same task"
        )
