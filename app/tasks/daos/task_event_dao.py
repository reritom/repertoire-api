from datetime import datetime
from typing import Optional

from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task import Task
from app.tasks.models.task_event import TaskEvent, TaskEventAround


class TaskEventDao(BaseDao[TaskEvent]):
    class Meta:
        model = TaskEvent

    def create(
        self,
        task_id: int,
        around: TaskEventAround,
        at: Optional[datetime] = None,
    ) -> TaskEvent:
        task_event = TaskEvent(
            task_id=task_id,
            around=around,
            at=at,
        )

        with self.session.begin_nested():
            self.session.add(task_event)

        self.session.flush()
        return task_event

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        task_id: OptionalFilter[int] = NO_FILTER,
        user_id: OptionalFilter[int] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(TaskEvent.id == id)

        if task_id is not NO_FILTER:
            statement = statement.where(TaskEvent.task_id == task_id)

        if user_id is not NO_FILTER:
            statement = statement.where(TaskEvent.task.has(Task.user_id == user_id))

        return statement

    def delete(self, id: int, user_id: int):
        task_event = self.get(id=id, user_id=user_id)
        self.session.delete(task_event)
        self.session.flush()
