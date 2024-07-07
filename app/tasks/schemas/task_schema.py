from datetime import date as _date
from datetime import datetime, time
from typing import Annotated, Optional

from pydantic import model_validator
from pydantic.fields import Field
from pydantic.main import BaseModel
from pydantic_core import PydanticCustomError

from app.tasks.models.task import Task
from app.tasks.models.task_frequency import FrequencyPeriod, FrequencyType, Weekday
from app.tasks.models.task_until import UntilType


class TaskFrequencySchema(BaseModel):
    type: FrequencyType
    period: Annotated[FrequencyPeriod | None, Field(default=None)]
    amount: Annotated[
        int,
        Field(
            ge=1,
            description=(
                "The amount of times the task needs to be repeated for the given period."
            ),
        ),
    ]
    use_calendar_period: Annotated[
        bool,
        Field(
            default=True,
            description=(
                "For 'this' types, one can either use the calendar period, "
                "or a period starting from the date of task creation"
            ),
        ),
    ]
    once_on_date: Annotated[
        _date | None,
        Field(
            None,
            description=(
                "Optionally specify the date that the task should be performed on."
            ),
        ),
    ]
    once_per_weekday: Annotated[
        Weekday | None,
        Field(None, description="This can be defined for tasks that are once per week"),
    ]
    once_at_time: Annotated[
        time | None,
        Field(
            None,
            description=(
                "If the task is either once per week, "
                "or on a specific date, "
                "the datetime can optionally be specified here"
            ),
        ),
    ]


class TaskFrequencyCreationSchema(TaskFrequencySchema):
    @model_validator(mode="after")
    def validate(self):
        if self.type == FrequencyType.on:
            if self.period is not None:
                raise PydanticCustomError(
                    "expected_conditional_field",  # TODO should be unexpected?
                    "Period shouldn't be set for specific events",
                )

            if self.amount != 1:
                raise PydanticCustomError(
                    "invalid_conditional_field",
                    "Amount must be 1 when task is 'on' a specific date",
                )

            if self.once_on_date is None:
                raise PydanticCustomError(
                    "expected_conditional_field",
                    "Specific date must be set",
                )

            # The once_at_time can be specified, but others should not be
            if self.once_per_weekday is not None:
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Unexpected value set: once per weekday should not defined",
                )

        elif self.type == FrequencyType.per:
            if self.period is None:
                raise PydanticCustomError(
                    "expected_conditional_field",
                    "Period must be set",
                )

            if self.amount != 1 and any(
                [self.once_at_time, self.once_on_date, self.once_per_weekday]
            ):
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Specific dates, times, days, are only supported when the frequency is once per period",
                )

            if self.once_per_weekday and self.period != FrequencyPeriod.week:
                # TODO perhaps could support a generic prefered weekday for other periods too
                raise PydanticCustomError(
                    "invalid_conditional_field",
                    "Specific weekday requires the period to be weekly",
                )

        elif self.type == FrequencyType.this:
            if self.period is None:
                raise PydanticCustomError(
                    "expected_conditional_field",
                    "Period must be set",
                )

            if any([self.once_at_time, self.once_on_date, self.once_per_weekday]):
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Unexpected value set: once at time, once on date, and once per weekday should not be defined",
                )
        return self


class TaskUntilSchema(BaseModel):
    type: UntilType
    amount: Annotated[int | None, Field(None)]
    date: Annotated[_date | None, Field(None)]


class TaskUntilCreationSchema(TaskUntilSchema):
    @model_validator(mode="after")
    def validate(self):
        if self.type in [UntilType.completed, UntilType.stopped]:
            # Other fields should be empty
            if any([self.amount, self.date]):
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Amount and date must be none when creating a task that ends once completed or stopped",
                )

        elif self.type == UntilType.amount:
            # The date should be empty and the amount should be at least 1
            if self.date:
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Date must not be set when creating a task that ends after a certain amount",
                    # TODO perhaps we could support a task with a amount that also expires after a certain date
                )

            if self.amount is None or self.amount < 1:
                raise PydanticCustomError(
                    "expected_conditional_field",
                    "Until amount must be set and greater than zero",
                )

        elif self.type == UntilType.date:
            # The amount should be empty and the date should be set
            if self.amount:
                raise PydanticCustomError(
                    "unexpected_conditional_field",
                    "Amount must not be set when creating a task that ends after a certain date",
                    # TODO perhaps we could support a task with a date that also expires after a certain amount
                )

            if self.date is None:
                raise PydanticCustomError(
                    "expected_conditional_field",
                    "Until date must be set",
                )
        return self


class TaskCreationSchema(BaseModel):
    name: Annotated[str, Field(max_length=Task.name.type.length)]
    description: Annotated[str, Field(max_length=Task.description.type.length)]
    category_id: Annotated[int | None, Field(None)]
    frequency: TaskFrequencyCreationSchema
    until: TaskUntilCreationSchema


class TaskSchema(TaskCreationSchema):
    id: int
    created: datetime
    frequency: TaskFrequencySchema
    until: TaskUntilSchema
    next_event_datetime: Optional[datetime] = None
