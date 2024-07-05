from datetime import date

import pytest

from app.tasks.models.task_until import UntilType
from app.tasks.schemas.task_schema import TaskUntilCreationSchema


def test_task_until_creation_schema_ok__date():
    TaskUntilCreationSchema(
        type=UntilType.date,
        date=date(2023, 12, 25),
    )


def test_task_until_creation_schema_ok__amount():
    TaskUntilCreationSchema(
        type=UntilType.amount,
        amount=20,
    )


def test_task_until_creation_schema_ok__stopped():
    TaskUntilCreationSchema(
        type=UntilType.stopped,
    )


def test_task_until_creation_schema_ok__completed():
    TaskUntilCreationSchema(type=UntilType.completed)


def test_task_until_creation_schema_failure__amount__amount_not_set():
    with pytest.raises(ValueError) as ctx:
        TaskUntilCreationSchema(type=UntilType.amount)

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"] == "Until amount must be set and greater than zero"
    )


def test_task_until_creation_schema_failure__amount__date_set():
    with pytest.raises(ValueError) as ctx:
        TaskUntilCreationSchema(
            type=UntilType.amount,
            amount=10,
            date=date(2023, 12, 25),
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Date must not be set when creating a task that ends after a certain amount"
    )


def test_task_until_creation_schema_failure__date__date_not_set():
    with pytest.raises(ValueError) as ctx:
        TaskUntilCreationSchema(type=UntilType.date)

    assert ctx.value.error_count() == 1
    assert ctx.value.errors()[0]["msg"] == "Until date must be set"


def test_task_until_creation_schema_failure__date__amount_set():
    with pytest.raises(ValueError) as ctx:
        TaskUntilCreationSchema(
            type=UntilType.date,
            date=date(2023, 12, 25),
            amount=10,
        )

    assert ctx.value.error_count() == 1
    assert (
        ctx.value.errors()[0]["msg"]
        == "Amount must not be set when creating a task that ends after a certain date"
    )
