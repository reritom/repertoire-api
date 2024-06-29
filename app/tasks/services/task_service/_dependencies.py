from typing import Annotated

from fast_depends import Depends

from app.accounts.models.user import User
from app.database import SessionType
from app.shared.exceptions import ServiceValidationError
from app.tasks.daos.task_dao import TaskDao
from app.tasks.daos.task_frequency_dao import TaskFrequencyDao
from app.tasks.daos.task_until_dao import TaskUntilDao
from app.tasks.models.task import Task, TaskStatus
from app.tasks.schemas.task_schema import TaskCreationSchema
from app.tasks.services._dependencies import get_task as get_task_dependency
from app.tasks.services._dependencies import get_task_dao
from app.tasks.services.category_service import service as category_service


def get_task_name_from_task_creation_payload(
    task_creation_payload: Annotated[TaskCreationSchema, Depends],
) -> str:
    return task_creation_payload.name


def get_task_category_id_from_task_creation_payload(
    task_creation_payload: Annotated[TaskCreationSchema, Depends],
) -> int | None:
    return task_creation_payload.category_id


def validate_name_is_unique_for_task_creation(
    name: Annotated[str, Depends(get_task_name_from_task_creation_payload)],
    authenticated_user: User = Depends,
    task_dao: TaskDao = Depends(get_task_dao),
):
    # TODO maybe make case insensitive
    if task_dao.get(user_id=authenticated_user.id, name=name, raise_exc=False):
        raise ServiceValidationError("A task already exists with this name")


def validate_category_is_visible_for_task_creation(
    category_id: Annotated[
        int | None, Depends(get_task_category_id_from_task_creation_payload)
    ],
    session: SessionType,
    authenticated_user: User,
):
    if category_id:
        category_service.get_category(
            session=session,
            authenticated_user=authenticated_user,
            category_id=category_id,
        )


def validate_task_status_for_completion(
    task: Annotated[Task, Depends(get_task_dependency)],
):
    if task.status == TaskStatus.completed:
        raise ServiceValidationError("The task is already completed")


def validate_task_status_for_pause(task: Annotated[Task, Depends(get_task_dependency)]):
    if task.status != TaskStatus.ongoing:
        raise ServiceValidationError("Cannot pause a task that isn't ongoing")


def validate_task_status_for_unpause(
    task: Annotated[Task, Depends(get_task_dependency)],
):
    if task.status != TaskStatus.paused:
        raise ServiceValidationError("Cannot unpause a task that isn't paused")


def get_task_frequency_dao(session: SessionType = Depends) -> TaskFrequencyDao:
    return TaskFrequencyDao(session=session)


def get_task_until_dao(session: SessionType = Depends) -> TaskUntilDao:
    return TaskUntilDao(session=session)
