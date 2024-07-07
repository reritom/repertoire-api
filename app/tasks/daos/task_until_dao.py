from datetime import date
from typing import Optional

from app.shared.dao import BaseDao
from app.tasks.models.task_until import TaskUntil, UntilType


class TaskUntilDao(BaseDao[TaskUntil]):
    class Meta:
        model = TaskUntil

    def create(
        self,
        type: UntilType,
        amount: Optional[int] = None,
        date: Optional[date] = None,
    ) -> TaskUntil:
        until = TaskUntil(
            type=type,
            amount=amount,
            date=date,
        )

        with self.session.begin_nested():
            self.session.add(until)

        self.session.flush()
        return until

    def delete(self, id: int):
        statement = self.query().where(
            TaskUntil.id == id,
            TaskUntil.task == None,  # noqa: E711
        )
        until = self.perform_get(statement)
        self.session.delete(until)
        self.session.flush()
