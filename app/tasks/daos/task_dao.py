from datetime import date, datetime
from typing import Optional

from sqlalchemy import and_, nulls_last, update

from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, NO_OP, OptionalAction, OptionalFilter
from app.tasks.models.task import Task, TaskStatus
from app.tasks.models.task_until import TaskUntil, UntilType


class TaskDao(BaseDao[Task]):
    class Meta:
        model = Task
        default_order_by = (
            nulls_last(Task.next_event_datetime.asc()),
            Task.id.asc(),
        )

    def create(
        self,
        name: str,
        description: str,
        user_id: int,
        category_id: int,
        frequency_id: int,
        until_id: int,
    ) -> Task:
        task = Task(
            name=name,
            description=description,
            user_id=user_id,
            category_id=category_id,
            frequency_id=frequency_id,
            until_id=until_id,
        )

        with self.session.begin_nested():
            self.session.add(task)

        self.session.flush()
        return task

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        status: OptionalFilter[TaskStatus] = NO_FILTER,
        name: OptionalFilter[str] = NO_FILTER,
        category_id: OptionalFilter[Optional[int]] = NO_FILTER,
        user_id: OptionalFilter[int] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(Task.id == id)

        if status is not NO_FILTER:
            statement = statement.where(Task.status == status)

        if name is not NO_FILTER:
            statement = statement.where(Task.name == name)

        if category_id is not NO_FILTER:
            statement = statement.where(Task.category_id == category_id)

        if user_id is not NO_FILTER:
            statement = statement.where(Task.user_id == user_id)

        return statement

    def update(
        self,
        id: int,
        user_id: int,
        status: OptionalAction[TaskStatus] = NO_OP,
        manually_completed_at: Optional[datetime] = NO_OP,
        next_event_datetime: OptionalAction[datetime] = NO_OP,
        frequency_id: OptionalAction[int] = NO_OP,
        until_id: OptionalAction[int] = NO_OP,
    ):
        task = self.get(id=id, user_id=user_id)

        if status != NO_OP:
            task.status = status
            self.session.add(task)
            self.session.flush()

        if manually_completed_at != NO_OP:
            task.manually_completed_at = manually_completed_at
            self.session.add(task)
            self.session.flush()

        if next_event_datetime != NO_OP:
            task.next_event_datetime = next_event_datetime
            self.session.add(task)
            self.session.flush()

        if frequency_id != NO_OP:
            task.frequency_id = frequency_id
            self.session.add(task)
            self.session.flush()

        if until_id != NO_OP:
            task.until_id = until_id
            self.session.add(task)
            self.session.flush()

    def delete(self, id: int, user_id: int):
        task = self.get(id=id, user_id=user_id)
        self.session.delete(task)
        self.session.flush()

    def mark_ongoing_date_tasks_as_completed(self):
        # Any ongoing or paused task that has reached the
        # expiration date will be updated to completed
        self.session.execute(
            update(Task)
            .where(
                Task.status != TaskStatus.completed,
                Task.until.has(
                    and_(
                        TaskUntil.type == UntilType.date, TaskUntil.date <= date.today()
                    )
                ),
            )
            .values({"status": TaskStatus.completed, "next_event_datetime": None})
        )
