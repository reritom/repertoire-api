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
