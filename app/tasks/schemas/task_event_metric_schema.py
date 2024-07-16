from decimal import Decimal
from typing import Annotated

from pydantic import BaseModel, Field

from app.shared.tools import decimal_serializer


class TaskEventMetricCreationSchema(BaseModel):
    task_metric_id: int
    task_event_id: int
    value: Annotated[Decimal, decimal_serializer] = Field(decimal_places=2)


class TaskEventMetricSchema(TaskEventMetricCreationSchema):
    id: int
