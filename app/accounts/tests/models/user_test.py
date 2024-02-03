from app.accounts.models.user import User
from app.accounts.models.user_preference import UserPreference
from app.accounts.tests.factories import UserFactory, UserPreferenceFactory
from app.tasks.models.category import Category
from app.tasks.models.task import Task
from app.tasks.tests.factories import (
    CategoryFactory,
    TaskFactory,
)


def test_delete_user_cascade_children(session):
    user = UserFactory()
    preference = UserPreferenceFactory(user=user)
    category = CategoryFactory(user=user)
    task = TaskFactory(category=category, user=user)

    session.delete(user)
    session.flush()

    assert session.get(User, user.id) is None
    assert session.get(UserPreference, preference.id) is None
    assert session.get(Category, category.id) is None
    assert session.get(Task, task.id) is None
