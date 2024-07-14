from fastapi.testclient import TestClient

from app.accounts.tests.factories import TEST_PASSWORD, UserFactory


def test_login_ok(client: TestClient):
    user = UserFactory()
    response = client.post(
        "/api/login", json={"email": user.email, "password": TEST_PASSWORD}
    )

    assert response.status_code == 201
    json = response.json()
    assert "token" in json
    assert "expires" in json


def test_login_failure_invalid_credentials(client: TestClient):
    user = UserFactory()
    response = client.post(
        "/api/login", json={"email": user.email, "password": "this-is-not-it"}
    )

    assert response.status_code == 400
    assert response.json() == {
        "message": "Invalid credentials",
        "type": "ServiceValidationError",
    }


def test_login_failure_missing_fields(client: TestClient):
    response = client.post("/api/login", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "loc": ["body", "email"],
                "msg": "Field required",
                "type": "missing",
            },
            {
                "loc": ["body", "password"],
                "msg": "Field required",
                "type": "missing",
            },
        ]
    }


def test_login_failure_already_logged_in(make_authenticated_client):
    client: TestClient = make_authenticated_client(UserFactory())
    response = client.post(
        "/api/login", json={"email": "myemail", "password": "mypassword"}
    )

    assert response.json() == {"detail": "Already authenticated"}
    assert response.status_code == 403
