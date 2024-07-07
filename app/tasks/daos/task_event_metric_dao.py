from decimal import Decimal

from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task import Task
from app.tasks.models.task_event import TaskEvent
from app.tasks.models.task_event_metric import TaskEventMetric


class TaskEventMetricDao(BaseDao[TaskEventMetric]):
    class Meta:
        model = TaskEventMetric

    def create(
        self,
        task_metric_id: int,
        task_event_id: int,
        value: Decimal,
    ) -> TaskEventMetric:
        event_metric = TaskEventMetric(
            task_metric_id=task_metric_id,
            task_event_id=task_event_id,
            value=value,
        )

        with self.session.begin_nested():
            self.session.add(event_metric)

        self.session.flush()
        return event_metric

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        task_id: OptionalFilter[int] = NO_FILTER,
        user_id: OptionalFilter[int] = NO_FILTER,
        task_event_id: OptionalFilter[int] = NO_FILTER,
        task_metric_id: OptionalFilter[int] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(TaskEventMetric.id == id)

        if task_id is not NO_FILTER:
            statement = statement.where(
                TaskEventMetric.task_event.has(TaskEvent.task_id == task_id)
            )

        if user_id is not NO_FILTER:
            statement = statement.where(
                TaskEventMetric.task_event.has(
                    TaskEvent.task.has(Task.user_id == user_id)
                )
            )

        if task_event_id is not NO_FILTER:
            statement = statement.where(TaskEventMetric.task_event_id == task_event_id)

        if task_metric_id is not NO_FILTER:
            statement = statement.where(
                TaskEventMetric.task_metric_id == task_metric_id
            )

        return statement

    def delete(self, id: int, user_id: int):
        event_metric = self.get(id=id, user_id=user_id)
        self.session.delete(event_metric)
        self.session.flush()
