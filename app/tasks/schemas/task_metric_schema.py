from pydantic import BaseModel, Field

from app.tasks.models.task_metric import TaskMetric


class TaskMetricCreationSchema(BaseModel):
    task_id: int
    name: str = Field(..., max_length=TaskMetric.name.type.length)
    prompt: str = Field(..., max_length=TaskMetric.prompt.type.length)
    required: bool


class TaskMetricSchema(TaskMetricCreationSchema):
    id: int
