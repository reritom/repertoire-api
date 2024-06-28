import pytest
from sqlalchemy.exc import IntegrityError

from app.tasks.models.task_event import TaskEvent
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.models.task_metric import TaskMetric
from app.tasks.tests.factories import (
    TaskEventFactory,
    TaskEventMetricFactory,
    TaskMetricFactory,
)


def test_create_failure_duplicate_metric_name_for_task(session):
    existing = TaskMetricFactory()

    task_metric = TaskMetric(
        task=existing.task,
        name=existing.name,
        prompt="myprompt",
        required=True,
    )

    with pytest.raises(IntegrityError) as ctx:
        session.add(task_metric)
        session.flush()

    assert "unique_task_metric_name" in ctx.value.args[0]


def test_delete_task_metric_cascade(session):
    task_metric = TaskMetricFactory()
    task_event = TaskEventFactory()
    event_metric = TaskEventMetricFactory(
        task_event=task_event, task_metric=task_metric
    )

    session.delete(task_metric)
    session.flush()

    assert session.get(TaskMetric, task_metric.id) is None
    assert session.get(TaskEventMetric, event_metric.id) is None
    assert session.get(TaskEvent, task_event.id) is not None
