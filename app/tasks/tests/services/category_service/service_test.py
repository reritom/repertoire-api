import pytest
from sqlalchemy.exc import NoResultFound

from app.accounts.tests.factories import UserFactory
from app.shared.exceptions import ServiceValidationError
from app.tasks.models.category import Category, IconNameEnum
from app.tasks.schemas.category_schema import CategoryCreationSchema
from app.tasks.services.category_service.service import (
    create_category,
    delete_category,
    get_categories,
    get_category,
)
from app.tasks.tests.factories import CategoryFactory


def test_create_category_ok__no_parent(session):
    user = UserFactory()

    category = create_category(
        session=session,
        authenticated_user=user,
        category_creation_payload=CategoryCreationSchema(
            icon_name=IconNameEnum.swimming,
            icon_hex_colour="FFFFFF",
            name="aqua",
            description="aqua activities",
        ),
    )

    assert category.name == "aqua"
    assert category.description == "aqua activities"
    assert category.icon_name == IconNameEnum.swimming
    assert category.icon_hex_colour == "FFFFFF"


def test_create_category_ok__with_parent(session):
    user = UserFactory()
    parent = CategoryFactory(user=user)

    category = create_category(
        session=session,
        authenticated_user=user,
        category_creation_payload=CategoryCreationSchema(
            icon_name=IconNameEnum.swimming,
            icon_hex_colour="FFFFFF",
            name="aqua",
            description="aqua activities",
            parent_category_id=parent.id,
        ),
    )

    assert category.name == "aqua"
    assert category.description == "aqua activities"
    assert category.icon_name == IconNameEnum.swimming
    assert category.icon_hex_colour == "FFFFFF"
    assert category.parent_category_id == parent.id


def test_create_category_failure__parent_not_visible_to_user(session):
    user = UserFactory()
    parent = CategoryFactory()

    with pytest.raises(ServiceValidationError) as ctx:
        create_category(
            session=session,
            authenticated_user=user,
            category_creation_payload=CategoryCreationSchema(
                icon_name=IconNameEnum.swimming,
                icon_hex_colour="FFFFFF",
                name="aqua",
                description="aqua activities",
                parent_category_id=parent.id,
            ),
        )

    assert ctx.value.args[0] == "Parent category is invalid"


def test_create_category_failure__name_not_unique(session):
    user = UserFactory()
    existing = CategoryFactory(user=user)

    with pytest.raises(ServiceValidationError) as ctx:
        create_category(
            session=session,
            authenticated_user=user,
            category_creation_payload=CategoryCreationSchema(
                icon_name=IconNameEnum.swimming,
                icon_hex_colour="FFFFFF",
                name=existing.name,
                description="aqua activities",
            ),
        )

    assert ctx.value.args[0] == "A category already exists with this name"


@pytest.mark.skip("Not implemented")
def test_create_category_failure__name_not_unique_integrity_error():
    ...


def test_get_category_ok(session):
    user = UserFactory()
    category = CategoryFactory(user=user)

    retrieved = get_category(
        session=session,
        category_id=category.id,
        authenticated_user=user,
    )

    assert retrieved == category


def test_get_category_failure__not_visible_to_user(session):
    user = UserFactory()
    category = CategoryFactory()

    with pytest.raises(NoResultFound):
        get_category(
            session=session,
            category_id=category.id,
            authenticated_user=user,
        )


def test_list_categories_ok(session):
    # Noise
    CategoryFactory.create_batch(5)

    user = UserFactory()
    category = CategoryFactory(user=user)

    retrieved = get_categories(session=session, authenticated_user=user)

    assert retrieved == [category]


def test_delete_category_ok(session):
    user = UserFactory()
    category = CategoryFactory(user=user)

    delete_category(
        session=session,
        category_id=category.id,
        authenticated_user=user,
    )

    assert session.get(Category, category.id) is None


def test_delete_category_failure__not_visible_to_user(session):
    user = UserFactory()
    category = CategoryFactory()

    with pytest.raises(NoResultFound):
        delete_category(
            session=session,
            category_id=category.id,
            authenticated_user=user,
        )
