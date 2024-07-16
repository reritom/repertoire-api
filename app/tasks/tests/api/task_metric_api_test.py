from fastapi.testclient import TestClient

from app.accounts.tests.factories import UserFactory
from app.tasks.models.task_metric import TaskMetric
from app.tasks.tests.factories import TaskFactory, TaskMetricFactory


def test_create_task_metric_failure_not_authenticated(client: TestClient):
    response = client.post("/api/task-metrics", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_create_task_metric_failure_missing_fields(client: TestClient, using_user):
    with using_user(UserFactory()):
        response = client.post("/api/task-metrics", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["body", "task_id"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "name"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "prompt"], "msg": "Field required"},
            {"type": "missing", "loc": ["body", "required"], "msg": "Field required"},
        ]
    }


def test_create_task_metric_failure_task_not_visible_to_user(
    client: TestClient, using_user
):
    task = TaskFactory()

    with using_user(UserFactory()):
        response = client.post(
            "/api/task-metrics",
            json={
                "task_id": task.id,
                "name": "laps",
                "prompt": "How many laps?",
                "required": False,
            },
        )

    # TODO this should maybe be a 400 service validation error
    assert response.status_code == 404
    assert response.json() == {
        "message": "Task not found",
        "type": "NoResultFound",
    }


def test_create_task_metric_ok(client: TestClient, using_user):
    user = UserFactory()
    task = TaskFactory(user=user)

    with using_user(user):
        response = client.post(
            "/api/task-metrics",
            json={
                "task_id": task.id,
                "name": "laps",
                "prompt": "How many laps?",
                "required": False,
            },
        )

    assert response.status_code == 201
    response_json = response.json()
    assert response_json == {
        "task_id": task.id,
        "name": "laps",
        "prompt": "How many laps?",
        "required": False,
        "id": response_json["id"],
    }


def test_get_task_metrics_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-metrics")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_metrics_failure_missing_required_filter(
    client: TestClient, using_user
):
    with using_user(UserFactory()):
        response = client.get("/api/task-metrics")

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {"type": "missing", "loc": ["query", "task_id"], "msg": "Field required"}
        ]
    }


def test_get_task_metrics_ok(client: TestClient, using_user):
    user = UserFactory()
    TaskMetricFactory(task__user=user)  # Noise
    task_metric = TaskMetricFactory(task__user=user)

    with using_user(user):
        response = client.get(
            "/api/task-metrics", params={"task_id": task_metric.task_id}
        )

    assert response.status_code == 200
    assert response.json() == [
        {
            "task_id": task_metric.task_id,
            "name": task_metric.name,
            "prompt": task_metric.prompt,
            "required": task_metric.required,
            "id": task_metric.id,
        }
    ]


def test_get_task_metric_failure_not_authenticated(client: TestClient):
    response = client.get("/api/task-metrics/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_task_metric_failure_not_visible_to_user(client: TestClient, using_user):
    task_metric = TaskMetricFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/task-metrics/{task_metric.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Metric not found",
        "type": "NoResultFound",
    }


def test_get_task_metric_ok(client: TestClient, using_user):
    user = UserFactory()
    task_metric = TaskMetricFactory(task__user=user)

    with using_user(user):
        response = client.get(f"/api/task-metrics/{task_metric.id}")

    assert response.status_code == 200
    assert response.json() == {
        "task_id": task_metric.task_id,
        "name": task_metric.name,
        "prompt": task_metric.prompt,
        "required": task_metric.required,
        "id": task_metric.id,
    }


def test_delete_task_metric_failure_not_authenticated(client: TestClient):
    response = client.delete("/api/task-metrics/12345")

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_delete_task_metric_failure_not_visible_to_user(client: TestClient, using_user):
    task_metric = TaskMetricFactory()

    with using_user(UserFactory()):
        response = client.delete(f"/api/task-metrics/{task_metric.id}")

    assert response.status_code == 404
    assert response.json() == {
        "message": "Task Metric not found",
        "type": "NoResultFound",
    }


def test_delete_task_metric_ok(client: TestClient, using_user, session):
    user = UserFactory()
    task_metric = TaskMetricFactory(task__user=user)

    with using_user(user):
        response = client.delete(f"/api/task-metrics/{task_metric.id}")

    assert response.status_code == 204
    assert session.get(TaskMetric, task_metric.id) is None
