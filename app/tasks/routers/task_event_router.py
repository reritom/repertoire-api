from typing import List

from fastapi import APIRouter, Depends, Path, Query

from app.accounts.models.user import User
from app.auth.routers.dependencies import (
    authenticated_user_required,
    get_authenticated_user,
)
from app.database import SessionType, get_session
from app.tasks.models.task_event import TaskEvent
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema, TaskEventSchema
from app.tasks.services.task_event_service import service as task_event_service

router = APIRouter(
    tags=["Task events"], dependencies=[Depends(authenticated_user_required)]
)


@router.post(
    "/task-events",
    response_model=TaskEventSchema,
    status_code=201,
)
def create_task_event(
    payload: TaskEventCreationSchema,
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskEvent:
    return task_event_service.create_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_creation_payload=payload,
    )


@router.get(
    "/task-events",
    response_model=List[TaskEventSchema],
    status_code=200,
)
def get_task_events(
    # TODO maybe make task_id optionally to support stuff like "Get all events for this category for this period"
    task_id: int = Query(...),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> List[TaskEvent]:
    return task_event_service.get_task_events(
        session=session,
        authenticated_user=authenticated_user,
        task_id=task_id,
    )


@router.get(
    "/task-events/{task_event_id}",
    response_model=TaskEventSchema,
    status_code=200,
)
def get_task_event(
    task_event_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> TaskEvent:
    return task_event_service.get_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_id,
    )


@router.delete(
    "/task-events/{task_event_id}",
    response_model=None,
    status_code=204,
)
def delete_task_event(
    task_event_id: int = Path(),
    session: SessionType = Depends(get_session),
    authenticated_user: User = Depends(get_authenticated_user),
) -> None:
    return task_event_service.delete_task_event(
        session=session,
        authenticated_user=authenticated_user,
        task_event_id=task_event_id,
    )
