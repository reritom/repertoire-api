from fastapi.testclient import TestClient

from app.accounts.tests.factories import UserFactory
from app.tasks.models.category import Category
from app.tasks.tests.factories import CategoryFactory


def test_create_category_ok__no_parent(client: TestClient, using_user):
    # Noise
    CategoryFactory(name="myname")

    user = UserFactory()

    with using_user(user):
        response = client.post(
            "/api/categories",
            json={
                "name": "myname",
                "description": "mydesc",
                "icon_name": "swimming",
                "icon_hex_colour": "FFFFFF",
            },
        )

    assert response.status_code == 201
    assert response.json() == {
        "icon_name": "swimming",
        "name": "myname",
        "description": "mydesc",
        "icon_hex_colour": "FFFFFF",
        "parent_category_id": None,
        "id": response.json()["id"],
    }


def test_create_category_failure_missing_fields(client: TestClient, using_user):
    user = UserFactory()

    with using_user(user):
        response = client.post("/api/categories", json={})

    assert response.status_code == 422
    assert response.json() == {
        "detail": [
            {
                "type": "missing",
                "loc": ["body", "icon_name"],
                "msg": "Field required",
            },
            {
                "type": "missing",
                "loc": ["body", "name"],
                "msg": "Field required",
            },
            {
                "type": "missing",
                "loc": ["body", "description"],
                "msg": "Field required",
            },
            {
                "type": "missing",
                "loc": ["body", "icon_hex_colour"],
                "msg": "Field required",
            },
        ]
    }


def test_create_category_failure_not_authenticated(client: TestClient):
    response = client.post("/api/categories", json={})

    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_create_category_failure_duplicate_name(client: TestClient, using_user):
    existing = CategoryFactory()

    with using_user(existing.user):
        response = client.post(
            "/api/categories",
            json={
                "name": existing.name,
                "description": "mydesc",
                "icon_name": "swimming",
                "icon_hex_colour": "FFFFFF",
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "message": "A category already exists with this name",
        "type": "ServiceValidationError",
    }


def test_create_category_failure_parent_not_visible_to_user(
    client: TestClient, using_user
):
    not_visible_category = CategoryFactory()

    with using_user(UserFactory()):
        response = client.post(
            "/api/categories",
            json={
                "name": "myname",
                "description": "mydesc",
                "icon_name": "swimming",
                "icon_hex_colour": "FFFFFF",
                "parent_category_id": not_visible_category.id,
            },
        )

    assert response.status_code == 400
    assert response.json() == {
        "message": "Parent category is invalid",
        "type": "ServiceValidationError",
    }


def test_get_categories_ok(client: TestClient, using_user):
    CategoryFactory()  # Noise

    user = UserFactory()
    category = CategoryFactory(user=user)

    with using_user(user):
        response = client.get("/api/categories")

    assert response.status_code == 200
    assert response.json() == [
        {
            "icon_name": category.icon_name.value,
            "name": category.name,
            "description": category.description,
            "icon_hex_colour": category.icon_hex_colour,
            "parent_category_id": category.parent_category_id,
            "id": category.id,
        }
    ]


def test_get_categories_failure_not_authenticated(client: TestClient):
    response = client.get("/api/categories")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_category_ok(client: TestClient, using_user):
    user = UserFactory()
    category = CategoryFactory(user=user)

    with using_user(user):
        response = client.get(f"/api/categories/{category.id}")

    assert response.status_code == 200
    assert response.json() == {
        "icon_name": category.icon_name.value,
        "name": category.name,
        "description": category.description,
        "icon_hex_colour": category.icon_hex_colour,
        "parent_category_id": category.parent_category_id,
        "id": category.id,
    }


def test_get_category_failure_not_authenticated(client: TestClient):
    response = client.get("/api/categories/12345")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_get_category_failure_not_visible_to_user(client: TestClient, using_user):
    category = CategoryFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/categories/{category.id}")

    assert response.status_code == 404
    assert response.json() == {"message": "Category not found", "type": "NoResultFound"}


def test_delete_category_ok(client: TestClient, using_user, session):
    user = UserFactory()
    category = CategoryFactory(user=user)

    with using_user(user):
        response = client.delete(f"/api/categories/{category.id}")

    assert response.status_code == 204
    assert session.get(Category, category.id) is None


def test_delete_category_failure_not_authenticated(client: TestClient):
    response = client.delete("/api/categories/12345")
    assert response.status_code == 401
    assert response.json() == {"detail": "Authentication required"}


def test_delete_category_failure_not_visible_to_user(client: TestClient, using_user):
    category = CategoryFactory()

    with using_user(UserFactory()):
        response = client.get(f"/api/categories/{category.id}")

    assert response.status_code == 404
    assert response.json() == {"message": "Category not found", "type": "NoResultFound"}
