from datetime import date

import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_until_dao import TaskUntilDao
from app.tasks.models.task_until import TaskUntil, UntilType
from app.tasks.tests.factories import TaskFactory, TaskUntilFactory


def test_create_task_until_ok(session):
    until = TaskUntilDao(session=session).create(
        type=UntilType.amount,
        amount=10,
        date=date(2020, 12, 25),
    )

    assert until.type == UntilType.amount
    assert until.amount == 10
    assert until.date == date(2020, 12, 25)


def test_delete_task_until_ok(session):
    # Noise
    UserFactory.create_batch(3)
    TaskUntilFactory.create_batch(4)

    until = TaskUntilFactory()

    TaskUntilDao(session=session).delete(id=until.id)

    assert session.get(TaskUntil, until.id) is None


def test_delete_task_until_failure_used_by_task(session):
    task = TaskFactory()
    until = task.until

    with pytest.raises(NoResultFound):
        # TODO maybe raise an integrity error
        TaskUntilDao(session=session).delete(id=until.id)
