import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.tests.factories import UserFactory
from app.tasks.models.category import Category, IconNameEnum
from app.tasks.tests.factories import CategoryFactory, TaskFactory


def test_create_category_ok(session):
    # Noise, category with the same name but a different user
    existing = CategoryFactory()

    user = UserFactory()
    new = Category(
        name=existing.name,
        user=user,
        description="mydescription",
        icon_name=IconNameEnum.swimming,
        icon_hex_colour="ffffff",
    )

    session.add(new)
    session.flush()

    assert (
        new is not None
    )  # Dummy, if there were an issue an exception would be raised on the flush


def test_create_category_failure_duplicate_name(session):
    existing = CategoryFactory()

    new = Category(
        name=existing.name,
        user=existing.user,
        description="mydescription",
        icon_name=IconNameEnum.swimming,
        icon_hex_colour="ffffff",
    )

    session.add(new)

    with pytest.raises(IntegrityError) as ctx:
        session.flush()

    assert "unique_user_category_name" in ctx.value.args[0]


def test_delete_category_no_cascade(session):
    category = CategoryFactory()
    task = TaskFactory(category=category)

    session.delete(category)
    session.flush()
    session.refresh(task)

    assert task is not None
