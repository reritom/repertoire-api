from fastapi.testclient import TestClient

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task_event_metric import TaskEventMetric
from app.tasks.tests.factories import (
    TaskEventFactory,
    TaskEventMetricFactory,
    TaskFactory,
    TaskMetricFactory,
)


def test_create_task_event_metric_failure_not_authenticated(client: TestClient):
    response = client.post("/api/task-event-metrics", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_create_task_event_metric_failure_missing_fields(
    client: TestClient, using_user
):
    with using_user(UserFactory()):
        response = client.post("/api/task-event-metrics", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "task_metric_id"],
                "msg": "Field required",
            },
            {
                "type": "missing",
                "loc": ["body", "task_event_id"],
                "msg": "Field required",
            },
            {"type": "missing", "loc": ["body", "value"], "msg": "Field required"},
        ]
    }


def test_create_task_event_metric_failure_task_not_visible_to_user(
    client: TestClient, using_user
):
    task = TaskFactory()
    event = TaskEventFactory(task=task)
    metric = TaskMetricFactory(task=task)

    with using_user(UserFactory()):
        response = client.post(
            "/api/task-event-metrics",
            json={
                "task_event_id": event.id,
                "task_metric_id": metric.id,
                "value": 10,
            },
        )

    # TODO this should maybe be a 400 service validation error
    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Event not found",
        "type": "NoResultFound",
    }


def test_create_task_event_metric_ok(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user)
    event = TaskEventFactory(task=task)
    metric = TaskMetricFactory(task=task)

    with using_user(user):
        response = client.post(
            "/api/task-event-metrics",
            json={
                "task_event_id": event.id,
                "task_metric_id": metric.id,
                "value": "10.90",
            },
        )

    assert response.status_code == 201
    response_json = response.json()
    assert response_json == {
        "task_event_id": event.id,
        "task_metric_id": metric.id,
        "value": "10.90",
        "id": response_json["id"],
    }


def test_get_task_event_metrics_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-event-metrics")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


# TODO test filters


def test_get_task_event_metrics_ok(client: TestClient, using_user):
    user = UserFactory()
    TaskEventMetricFactory()  # Noise
    task_event_metric = TaskEventMetricFactory(task__user=user)

    with using_user(user):
        response = client.get("/api/task-event-metrics")

    assert response.status_code == 200
    assert response.json() == [
        {
            "task_event_id": task_event_metric.task_event_id,
            "task_metric_id": task_event_metric.task_metric_id,
            "value": f"{task_event_metric.value:.2f}",
            "id": task_event_metric.id,
        }
    ]


def test_get_task_event_metric_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-event-metrics/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_event_metric_failure_not_visible_to_user(
    client: TestClient, using_user
):
    task_event_metric = TaskEventMetricFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/task-event-metrics/{task_event_metric.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Event Metric not found",
        "type": "NoResultFound",
    }


def test_get_task_event_metric_ok(client: TestClient, using_user):
    user = UserFactory()
    task_event_metric = TaskEventMetricFactory(task__user=user)

    with using_user(user):
        response = client.get(f"/api/task-event-metrics/{task_event_metric.id}")

    assert response.status_code == 200
    assert response.json() == {
        "task_event_id": task_event_metric.task_event_id,
        "task_metric_id": task_event_metric.task_metric_id,
        "value": f"{task_event_metric.value:.2f}",
        "id": task_event_metric.id,
    }


def test_delete_task_event_metric_failure_not_authenticated(client: TestClient):
    response = client.delete("/api/task-event-metrics/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_delete_task_event_metric_failure_not_visible_to_user(
    client: TestClient, using_user
):
    task_event_metric = TaskEventMetricFactory()

    with using_user(UserFactory()):
        response = client.delete(f"/api/task-event-metrics/{task_event_metric.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Event Metric not found",
        "type": "NoResultFound",
    }


def test_delete_task_event_metric_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task_event_metric = TaskEventMetricFactory(task__user=user)

    with using_user(user):
        response = client.delete(f"/api/task-event-metrics/{task_event_metric.id}")

    assert response.status_code == 204
    assert session.get(TaskEventMetric, task_event_metric.id) is None
