import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.task_metric_dao import TaskMetricDao
from app.tasks.models.task_metric import TaskMetric
from app.tasks.tests.factories import TaskEventFactory, TaskFactory, TaskMetricFactory


def test_create_task_metric_ok(session):
    # Noise
    UserFactory.create_batch(2)
    TaskFactory.create_batch(3)
    TaskMetricFactory(name="myname")  # Under a diferent task, so its ok

    task = TaskFactory()

    task_metric = TaskMetricDao(session=session).create(
        task_id=task.id,
        name="myname",
        prompt="enter my value",
        required=True,
    )

    assert task_metric.task == task
    assert task_metric.name == "myname"
    assert task_metric.prompt == "enter my value"
    assert task_metric.required is True


def test_create_task_metric_failure_duplicate_name(session):
    user = UserFactory()
    task = TaskFactory(user=user)
    TaskMetricFactory(task=task, name="myname")

    with pytest.raises(IntegrityError) as ctx:
        TaskMetricDao(session=session).create(
            task_id=task.id,
            name="myname",
            prompt="enter my value",
            required=True,
        )

    assert "unique_task_metric_name" in ctx.value.args[0]


def test_query_filter_by_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    UserFactory.create_batch(3)

    task_metric_1 = TaskMetricFactory()
    task_metric_2 = TaskMetricFactory()

    cases = [
        ({}, [task_metric_1, task_metric_2]),
        ({"id": task_metric_1.id}, [task_metric_1]),
    ]

    for filters, expected_task_metrics in cases:
        with subtests.test():
            task_metrics = TaskMetricDao(session=session).list(**filters)
            assert task_metrics == expected_task_metrics


def test_query_filter_by_name(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    UserFactory.create_batch(3)

    task_metric_1 = TaskMetricFactory()
    task_metric_2 = TaskMetricFactory()

    cases = [
        ({}, [task_metric_1, task_metric_2]),
        ({"name": task_metric_1.name}, [task_metric_1]),
    ]

    for filters, expected_task_metrics in cases:
        with subtests.test():
            task_metrics = TaskMetricDao(session=session).list(**filters)
            assert task_metrics == expected_task_metrics


def test_query_filter_by_task_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    UserFactory.create_batch(3)

    task_metric_1 = TaskMetricFactory()
    task_metric_2 = TaskMetricFactory()

    cases = [
        ({}, [task_metric_1, task_metric_2]),
        ({"task_id": task_metric_1.task_id}, [task_metric_1]),
    ]

    for filters, expected_task_metrics in cases:
        with subtests.test():
            task_metrics = TaskMetricDao(session=session).list(**filters)
            assert task_metrics == expected_task_metrics


def test_query_filter_by_user_id(session, subtests):
    # Noise
    TaskFactory.create_batch(1)
    TaskEventFactory.create_batch(2)
    UserFactory.create_batch(3)

    task_metric_1 = TaskMetricFactory()
    task_metric_2 = TaskMetricFactory()

    cases = [
        ({}, [task_metric_1, task_metric_2]),
        ({"user_id": task_metric_1.task.user_id}, [task_metric_1]),
    ]

    for filters, expected_task_metrics in cases:
        with subtests.test():
            task_metrics = TaskMetricDao(session=session).list(**filters)
            assert task_metrics == expected_task_metrics


def test_delete_ok(session):
    task_metric = TaskMetricFactory()

    TaskMetricDao(session=session).delete(
        id=task_metric.id, user_id=task_metric.task.user_id
    )

    assert session.get(TaskMetric, task_metric.id) is None
