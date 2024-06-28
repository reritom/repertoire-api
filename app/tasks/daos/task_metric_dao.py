from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter
from app.tasks.models.task import Task
from app.tasks.models.task_metric import TaskMetric


class TaskMetricDao(BaseDao[TaskMetric]):
    class Meta:
        model = TaskMetric

    def create(
        self, task_id: int, name: str, prompt: str, required: bool
    ) -> TaskMetric:
        task_metric = TaskMetric(
            task_id=task_id,
            name=name,
            prompt=prompt,
            required=required,
        )

        with self.session.begin_nested():
            self.session.add(task_metric)

        self.session.flush()
        return task_metric

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        task_id: OptionalFilter[int] = NO_FILTER,
        user_id: OptionalFilter[int] = NO_FILTER,
        name: OptionalFilter[str] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(TaskMetric.id == id)

        if task_id is not NO_FILTER:
            statement = statement.where(TaskMetric.task_id == task_id)

        if user_id is not NO_FILTER:
            statement = statement.where(TaskMetric.task.has(Task.user_id == user_id))

        if name is not NO_FILTER:
            statement = statement.where(TaskMetric.name == name)

        return statement

    def delete(self, id: int, user_id: int):
        task_metric = self.get(id=id, user_id=user_id)
        self.session.delete(task_metric)
        self.session.flush()
