from typing import Annotated

from fast_depends.use import Depends, inject
from pydantic.functional_validators import SkipValidation
from sqlalchemy import Select, select

from app.accounts.models.user import User
from app.database import Session
from app.tasks.models.task import Task, TaskStatus


@inject
def create_task():
    ...


def get_scoped_tasks_statement(authenticated_user: Annotated[User, Depends]) -> Select:
    return select(Task).where(Task.user_id == authenticated_user.id)


def _get_task(
    statement: Annotated[Select, Depends(get_scoped_tasks_statement)],
    task_id: Annotated[int, Depends],
    session: Annotated[Session, Depends],
) -> Task:
    statement = statement.where(Task.id == task_id)
    return session.scalars(statement).one()


@inject
def get_task(task: Annotated[Task, Depends(_get_task)]) -> Task:
    return task


@inject
def get_tasks():
    ...


def validate_task_status_for_completion(task: Annotated[Task, Depends(get_task)]):
    if task.status == TaskStatus.completed:
        raise ValueError("The task is already completed")


@inject(extra_dependencies=[Depends(validate_task_status_for_completion)])
def complete_task(
    task: Annotated[Task, Depends(get_task)],
    session: Annotated[SkipValidation[Session], Depends],
):
    task.status = TaskStatus.completed
    session.add(task)
    session.commit()


def validate_task_is_active(task: Annotated[Task, Depends(_get_task)]):
    if task.status != TaskStatus.ongoing:
        raise ValueError("Cannot pause a task that isn't ongoing")


@inject(extra_dependencies=[Depends(validate_task_is_active)])
def pause_task(
    task: Annotated[Task, Depends(_get_task)],
    session: Annotated[SkipValidation[Session], Depends],
):
    task.status = TaskStatus.paused
    session.add(task)
    session.commit()


def validate_task_is_paused(task: Annotated[Task, Depends(get_task)]):
    if task.status != TaskStatus.paused:
        raise ValueError("Cannot unpause a task that isn't paused")


@inject(extra_dependencies=[Depends(validate_task_is_paused)])
def unpause_task(
    task: Annotated[Task, Depends(get_task)],
    session: Annotated[SkipValidation[Session], Depends],
) -> None:
    task.status = TaskStatus.ongoing
    session.add(task)
    session.commit()
