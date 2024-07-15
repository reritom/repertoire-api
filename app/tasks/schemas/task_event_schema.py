from datetime import datetime
from typing import Annotated, Optional

from pydantic import BaseModel, model_validator
from pydantic_core import PydanticCustomError

from app.shared.tools import datetime_serialiser
from app.tasks.models.task_event import TaskEventAround


class TaskEventCreationSchema(BaseModel):
    task_id: int
    around: TaskEventAround
    at: Annotated[Optional[datetime], datetime_serialiser] = None

    @model_validator(mode="after")
    def validate(self):
        if self.around == TaskEventAround.specifically and not self.at:
            raise PydanticCustomError(
                "expected_conditional_field",
                "Expected value not set: Specific datetime should be set",
            )

        if self.around != TaskEventAround.specifically and self.at:
            raise PydanticCustomError(
                "unexpected_conditional_field",
                "Unexpected value set: Specific datetime should not be set",
            )

        return self


class TaskEventSchema(TaskEventCreationSchema):
    id: int
    effective_datetime: Annotated[datetime, datetime_serialiser]
    created: Annotated[datetime, datetime_serialiser]
