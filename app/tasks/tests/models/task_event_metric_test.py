import pytest
from sqlalchemy.exc import IntegrityError

from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.tests.factories import TaskEventMetricFactory


def test_create_task_event_metric_failure_duplicate(session):
    existing = TaskEventMetricFactory()

    new = TaskEventMetric(
        task_event=existing.task_event, task_metric=existing.task_metric, value=10
    )

    session.add(new)
    with pytest.raises(IntegrityError) as ctx:
        session.flush()

    assert "unique_tast_event_metric" in ctx.value.args[0]
