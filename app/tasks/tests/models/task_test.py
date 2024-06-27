import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.models.category import Category
from app.tasks.models.task import Task
from app.tasks.models.task_event import TaskEvent
from app.tasks.models.task_frequency import TaskFrequency
from app.tasks.models.task_until import TaskUntil
from app.tasks.tests.factories import (
    CategoryFactory,
    TaskEventFactory,
    TaskFactory,
    TaskFrequencyFactory,
    TaskUntilFactory,
)


def test_create_task_ok(session):
    # Noise, task with the same name but a different user
    existing = TaskFactory()

    user = UserFactory()
    new = Task(
        name=existing.name,
        description="",
        user=user,
        frequency=TaskFrequencyFactory(),
        until=TaskUntilFactory(),
    )

    session.add(new)
    session.flush()

    assert (
        new is not None
    )  # Dummy, if there were an issue an exception would be raised on the flush


def test_create_task_failure_duplicate_name(session):
    existing = TaskFactory()

    new = Task(
        name=existing.name,
        user=existing.user,
        description="",
        frequency=TaskFrequencyFactory(),
        until=TaskUntilFactory(),
    )

    session.add(new)

    with pytest.raises(IntegrityError) as ctx:
        session.flush()

    assert "unique_user_task_name" in ctx.value.args[0]


def test_delete_task_cascade_children(session):
    category = CategoryFactory()
    until = TaskUntilFactory()
    frequency = TaskFrequencyFactory()
    task = TaskFactory(category=category, until=until, frequency=frequency)
    event = TaskEventFactory(task=task)

    session.delete(task)
    session.flush()

    assert session.get(Category, category.id) is not None
    assert session.get(TaskUntil, until.id) is None
    assert session.get(TaskFrequency, frequency.id) is None
    assert session.get(Task, task.id) is None
    assert session.get(TaskEvent, event.id) is None
