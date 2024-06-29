from datetime import datetime

import pytest

from app.tasks.models.task_event import TaskEventAround
from app.tasks.schemas.task_event_schema import TaskEventCreationSchema


def test_task_event_creation_schema_ok__specifically():
    TaskEventCreationSchema(
        task_id=1,
        around=TaskEventAround.specifically,
        at=datetime(2025, 12, 25, 12, 0, 0),
    )


def test_task_event_creation_schema_ok__today():
    TaskEventCreationSchema(
        task_id=1,
        around=TaskEventAround.today,
        at=None,
    )


def test_task_event_creation_schema_failure__specifically_with_no_datetime():
    with pytest.raises(ValueError) as ctx:
        TaskEventCreationSchema(task_id=1, around=TaskEventAround.specifically, at=None)

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Expected value not set: Specific datetime should be set"
    )


def test_task_event_creation_schema_failure__today_with_datetime():
    with pytest.raises(ValueError) as ctx:
        TaskEventCreationSchema(
            task_id=1,
            around=TaskEventAround.today,
            at=datetime(2025, 12, 25, 12, 0, 0),
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Unexpected value set: Specific datetime should not be set"
    )
