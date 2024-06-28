from app.tasks.daos.task_event_metric_dao import TaskEventMetricDao
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.tests.factories import (
    TaskEventFactory,
    TaskEventMetricFactory,
    TaskFactory,
    TaskMetricFactory,
)


def test_create_task_event_metric_ok(session):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task = TaskFactory()
    task_event = TaskEventFactory(task=task)
    task_metric = TaskMetricFactory(task=task)

    task_event_metric = TaskEventMetricDao(session=session).create(
        task_metric_id=task_metric.id,
        task_event_id=task_event.id,
        value=10,
    )

    assert task_event_metric.task_event == task_event
    assert task_event_metric.task_metric == task_metric
    assert task_event_metric.value == 10


def test_query_filter_by_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task_event_metric_1 = TaskEventMetricFactory()
    task_event_metric_2 = TaskEventMetricFactory()

    cases = [
        ({}, [task_event_metric_1, task_event_metric_2]),
        ({"id": task_event_metric_1.id}, [task_event_metric_1]),
    ]

    for filters, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = TaskEventMetricDao(session=session).list(**filters)
            assert task_event_metrics == expected_task_event_metrics


def test_query_filter_by_task_event_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task_event_metric_1 = TaskEventMetricFactory()
    task_event_metric_2 = TaskEventMetricFactory()

    cases = [
        ({}, [task_event_metric_1, task_event_metric_2]),
        ({"task_event_id": task_event_metric_1.task_event_id}, [task_event_metric_1]),
    ]

    for filters, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = TaskEventMetricDao(session=session).list(**filters)
            assert task_event_metrics == expected_task_event_metrics


def test_query_filter_by_task_metric_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task_event_metric_1 = TaskEventMetricFactory()
    task_event_metric_2 = TaskEventMetricFactory()

    cases = [
        ({}, [task_event_metric_1, task_event_metric_2]),
        ({"task_metric_id": task_event_metric_1.task_metric_id}, [task_event_metric_1]),
    ]

    for filters, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = TaskEventMetricDao(session=session).list(**filters)
            assert task_event_metrics == expected_task_event_metrics


def test_query_filter_by_task_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task_event_metric_1 = TaskEventMetricFactory()
    task_event_metric_2 = TaskEventMetricFactory()

    cases = [
        ({}, [task_event_metric_1, task_event_metric_2]),
        ({"task_id": task_event_metric_1.task_metric.task_id}, [task_event_metric_1]),
    ]

    for filters, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = TaskEventMetricDao(session=session).list(**filters)
            assert task_event_metrics == expected_task_event_metrics


def test_query_filter_by_user_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    TaskMetricFactory.create_batch(3)

    task_event_metric_1 = TaskEventMetricFactory()
    task_event_metric_2 = TaskEventMetricFactory()

    cases = [
        ({}, [task_event_metric_1, task_event_metric_2]),
        (
            {"user_id": task_event_metric_1.task_metric.task.user_id},
            [task_event_metric_1],
        ),
    ]

    for filters, expected_task_event_metrics in cases:
        with subtests.test():
            task_event_metrics = TaskEventMetricDao(session=session).list(**filters)
            assert task_event_metrics == expected_task_event_metrics


def test_delete_ok(session):
    task_event_metric = TaskEventMetricFactory()

    TaskEventMetricDao(session=session).delete(
        id=task_event_metric.id,
        user_id=task_event_metric.task_event.task.user_id,
    )

    assert session.get(TaskEventMetric, task_event_metric.id) is None
