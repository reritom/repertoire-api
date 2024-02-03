from app.tasks.tests.factories import CategoryFactory, TaskFactory


def test_delete_category_no_cascade(session):
    category = CategoryFactory()
    task = TaskFactory(category=category)

    session.delete(category)
    session.flush()
    session.refresh(task)

    assert task is not None
