from datetime import date

import pytest

from app.tasks.models.task_until import TaskUntil, UntilType


@pytest.mark.parametrize(
    "until,expected_representation",
    [
        # Completed
        (TaskUntil(type=UntilType.completed), "Completed or I stop it"),
        # Stopped
        (TaskUntil(type=UntilType.stopped), "I stop it"),
        # Date
        (TaskUntil(type=UntilType.date, date=date(2020, 12, 25)), "2020-12-25"),
        # Amount
        (TaskUntil(type=UntilType.amount, amount=1), "Done once"),
        (TaskUntil(type=UntilType.amount, amount=2), "Done twice"),
        (TaskUntil(type=UntilType.amount, amount=3), "Done 3 times"),
    ],
)
def test_task_until_representation(until, expected_representation):
    assert until.representation == expected_representation
