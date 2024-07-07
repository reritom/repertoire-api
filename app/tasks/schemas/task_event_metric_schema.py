from decimal import Decimal

from pydantic import BaseModel


class TaskEventMetricCreationSchema(BaseModel):
    task_metric_id: int
    task_event_id: int
    value: Decimal


class TaskEventMetricSchema(TaskEventMetricCreationSchema):
    id: int
