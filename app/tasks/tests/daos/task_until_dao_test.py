from datetime import date

from app.tasks.daos.task_until_dao import TaskUntilDao
from app.tasks.models.task_until import UntilType


def test_create_task_until_ok(session):
    until = TaskUntilDao(session=session).create(
        type=UntilType.amount,
        amount=10,
        date=date(2020, 12, 25),
    )

    assert until.type == UntilType.amount
    assert until.amount == 10
    assert until.date == date(2020, 12, 25)
