from typing import Optional

from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task import Task, TaskStatus


class TaskDao(BaseDao[Task]):
    class Meta:
        model = Task

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

    def delete(self, id: int, user_id: int):
        task = self.get(id=id, user_id=user_id)
        self.session.delete(task)
        self.session.flush()
