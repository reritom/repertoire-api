from fast_depends import Depends

from app.database import SessionType
from app.shared.exceptions import ServiceValidationError
from app.tasks.daos.task_metric_dao import TaskMetricDao
from app.tasks.schemas.task_metric_schema import TaskMetricCreationSchema


def get_task_metric_dao(session: SessionType) -> TaskMetricDao:
    return TaskMetricDao(session=session)


def get_task_id_from_task_metric_creation_payload(
    task_metric_creation_payload: TaskMetricCreationSchema,
) -> int:
    return task_metric_creation_payload.task_id


def validate_task_metric_name_from_task_metric_creation_payload(
    task_metric_creation_payload: TaskMetricCreationSchema = Depends,
    task_metric_dao: TaskMetricDao = Depends(get_task_metric_dao),
):
    if task_metric_dao.get(
        task_id=task_metric_creation_payload.task_id,
        name=task_metric_creation_payload.name,
        raise_exc=False,
    ):
        raise ServiceValidationError(
            "A metric already exists with this name for this task"
        )
