import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.daos.category_dao import CategoryDao
from app.tasks.models.category import Category
from app.tasks.tests.factories import CategoryFactory


def test_category_create_ok(session):
    # Noise
    CategoryFactory.create_batch(3)
    UserFactory.create_batch(2)

    # Use a duplicate name but under another user
    existing = CategoryFactory()

    user = UserFactory()

    new = CategoryDao(session=session).create(
        user_id=user.id, name=existing.name, description="mydescription"
    )

    assert new.user == user
    assert new.name == existing.name
    assert new.description == "mydescription"


def test_category_create_failure_duplicate_name(session):
    existing = CategoryFactory()

    with pytest.raises(IntegrityError) as ctx:
        CategoryDao(session=session).create(
            user_id=existing.user_id, name=existing.name, description="mydescription"
        )

    assert "unique_user_category_name" in ctx.value.args[0]

    # To be sure we rolled back (an exception will be raises if not rolled back)
    session.commit()


def test_query_filter_by_id(session, subtests):
    category_1 = CategoryFactory()
    category_2 = CategoryFactory()

    cases = [
        ({}, [category_1, category_2]),
        ({"id": category_1.id}, [category_1]),
        ({"id": category_2.id}, [category_2]),
    ]

    for filters, expected_categories in cases:
        with subtests.test():
            categories = CategoryDao(session=session).list(**filters)
            assert categories == expected_categories


def test_query_filter_by_name(session, subtests):
    category_1 = CategoryFactory()
    category_2 = CategoryFactory()

    cases = [
        ({}, [category_1, category_2]),
        ({"name": category_1.name}, [category_1]),
        ({"name": category_2.name}, [category_2]),
    ]

    for filters, expected_categories in cases:
        with subtests.test():
            categories = CategoryDao(session=session).list(**filters)
            assert categories == expected_categories


def test_query_filter_by_user_id(session, subtests):
    category_1 = CategoryFactory()
    category_2 = CategoryFactory()

    cases = [
        ({}, [category_1, category_2]),
        ({"user_id": category_1.user_id}, [category_1]),
        ({"user_id": category_2.user_id}, [category_2]),
    ]

    for filters, expected_categories in cases:
        with subtests.test():
            categories = CategoryDao(session=session).list(**filters)
            assert categories == expected_categories


def test_delete_ok(session):
    category = CategoryFactory()

    CategoryDao(session=session).delete(id=category.id, user_id=category.user_id)

    assert session.get(Category, category.id) is None
