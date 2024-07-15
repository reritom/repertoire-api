from dataclasses import dataclass
from typing import List, Optional

from fastapi import APIRouter, Depends, Path
from fastapi.param_functions import Query

from app.accounts.models.user import User
from app.auth.routers.dependencies import (
    authenticated_user_required,
    get_authenticated_user,
)
from app.database import SessionType, get_session
from app.shared.tools import as_dict
from app.tasks.models.task import Task, TaskStatus
from app.tasks.schemas.task_schema import (
    TaskCreationSchema,
    TaskFrequencyCreationSchema,
    TaskSchema,
    TaskUntilCreationSchema,
)
from app.tasks.services.task_service import service as task_service

router = APIRouter(tags=["Tasks"], dependencies=[Depends(authenticated_user_required)])


@router.post(
    "/tasks",
    status_code=201,
    response_model=TaskSchema,
    description="Create a task",
)
def create_task(
    payload: TaskCreationSchema,
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Task:
    return task_service.create_task(
        session=session,
        authenticated_user=authenticated_user,
        task_creation_payload=payload,
    )


@dataclass
class TaskFilters:
    # Using dataclass instead of pydantic model as pydantic doesn't
    # distinguish None values from unset values, which is required for category_id
    # where None is a valid option

    # Technically Optional[TaskStatus] but it misleads the documentation
    # By saying status=None is acceptable when it isn't, and the null value is not passed to the service
    status: TaskStatus = Query(None)
    category_id: Optional[int] = Query(None)


@router.get(
    "/tasks",
    status_code=200,
    response_model=List[TaskSchema],
    description="Get all tasks",
)
def get_tasks(
    session: SessionType = Depends(get_session),
    filters: TaskFilters = Depends(TaskFilters),
    authenticated_user: User = Depends(get_authenticated_user),
) -> List[Task]:
    return task_service.get_tasks(
        session=session,
        authenticated_user=authenticated_user,
        **as_dict(filters),
    )


@router.get(
    "/tasks/{task_id}",
    status_code=200,
    response_model=TaskSchema,
    description="Get the given task",
)
def get_task(
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> Task:
    return task_service.get_task(
        task_id=task_id,
        session=session,
        authenticated_user=authenticated_user,
    )


@router.delete(
    "/tasks/{task_id}",
    status_code=204,
    response_model=None,
    description=(
        "Delete the task. "
        "This process can't be reversed and all child entities will be deleted too, "
        "including metrics, events, and notes"
    ),
)
def delete_task(
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.delete_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.post(
    "/tasks/{task_id}/pause",
    status_code=204,
    response_model=None,
    description="Pause the ongoing task",
)
def pause_task(
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.pause_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.post(
    "/tasks/{task_id}/unpause",
    status_code=204,
    response_model=None,
    description="Unpause the currently paused task",
)
def unpause_task(
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.unpause_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.post(
    "/tasks/{task_id}/complete",
    status_code=204,
    response_model=None,
    description="Mark the task as completed",
)
def complete_task(
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.complete_task(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.put(
    "/tasks/{task_id}/frequency",
    status_code=204,
    response_model=None,
    description="Update the task frequency",
)
def update_task_frequency(
    payload: TaskFrequencyCreationSchema,
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.update_task_frequency(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
        frequency_creation_payload=payload,
    )


@router.put(
    "/tasks/{task_id}/until",
    status_code=204,
    response_model=None,
    description="Update the task duration condition",
)
def update_task_until(
    payload: TaskUntilCreationSchema,
    task_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_service.update_task_until(
        session=session,
        task_id=task_id,
        authenticated_user=authenticated_user,
        until_creation_payload=payload,
    )
