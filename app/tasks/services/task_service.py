from typing import Annotated

from fast_depends.use import Depends, inject
from sqlalchemy import Select, select

from app.accounts.models.user import User
from app.database import Session
from app.tasks.models.category import Category
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_frequency import TaskFrequency
from app.tasks.models.task_until import TaskUntil
from app.tasks.schemas.task_schema import TaskCreationSchema


def get_scoped_tasks_statement(authenticated_user: Annotated[User, Depends]) -> Select:
    return select(Task).where(Task.user_id == authenticated_user.id)


def get_scoped_categories_statement(
    authenticated_user: Annotated[User, Depends],
) -> Select:
    return select(Category).where(Category.user_id == authenticated_user.id)


def _get_name(
    new_task: Annotated[TaskCreationSchema, Depends],
) -> str:
    return new_task.name


def _get_category_id(
    new_task: Annotated[TaskCreationSchema, Depends],
) -> int | None:
    return new_task.category_id


def validate_name_is_unique(
    name: Annotated[str, Depends(_get_name)],
    statement: Annotated[Select, Depends(get_scoped_tasks_statement)],
    session: Annotated[Session, Depends],
):
    # TODO maybe make case insensitive
    if session.scalars(statement.where(Task.name == name)).first():
        raise ValueError("A task already exists with this name")


def validate_category_is_visible(
    category_id: Annotated[int | None, Depends(_get_category_id)],
    statement: Annotated[Select, Depends(get_scoped_categories_statement)],
    session: Annotated[Session, Depends],
):
    if category_id:
        # TODO reraise as specific error
        session.scalars(statement.where(Category.id == category_id)).one()


@inject(
    extra_dependencies=[
        Depends(validate_name_is_unique),
        Depends(validate_category_is_visible),
    ]
)
def create_task(
    new_task: Annotated[TaskCreationSchema, Depends],
    authenticated_user: Annotated[User, Depends],
    session: Annotated[Session, Depends],
):
    task = Task(
        name=new_task.name,
        user=authenticated_user,
        description=new_task.description,
        category_id=new_task.category_id,
        frequency=TaskFrequency(
            type=new_task.frequency.type,
            period=new_task.frequency.period,
            amount=new_task.frequency.amount,
            once_on_date=new_task.frequency.once_on_date,
            once_per_weekday=new_task.frequency.once_per_weekday,
            once_at_time=new_task.frequency.once_at_time,
        ),
        until=TaskUntil(
            type=new_task.until.type,
            amount=new_task.until.amount,
            date=new_task.until.date,
        ),
    )
    session.add(task)
    session.commit()
    return task


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


class NoFilter:
    pass


@inject
def get_tasks(
    statement: Annotated[Select, Depends(get_scoped_tasks_statement)],
    session: Annotated[Session, Depends],
    status: TaskStatus | NoFilter = NoFilter,
    category_id: int | None | NoFilter = NoFilter,
):
    if status is not NoFilter:
        statement = statement.where(Task.status == status)

    if category_id is not NoFilter:
        statement = statement.where(Task.category_id == category_id)

    return session.scalars(statement.order_by(Task.id.asc())).all()


def validate_task_status_for_completion(task: Annotated[Task, Depends(_get_task)]):
    if task.status == TaskStatus.completed:
        raise ValueError("The task is already completed")


@inject(extra_dependencies=[Depends(validate_task_status_for_completion)])
def complete_task(
    task: Annotated[Task, Depends(_get_task)],
    session: Annotated[Session, Depends],
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
    session: Annotated[Session, Depends],
):
    task.status = TaskStatus.paused
    session.add(task)
    session.commit()


def validate_task_is_paused(task: Annotated[Task, Depends(_get_task)]):
    if task.status != TaskStatus.paused:
        raise ValueError("Cannot unpause a task that isn't paused")


@inject(extra_dependencies=[Depends(validate_task_is_paused)])
def unpause_task(
    task: Annotated[Task, Depends(_get_task)],
    session: Annotated[Session, Depends],
) -> None:
    task.status = TaskStatus.ongoing
    session.add(task)
    session.commit()
