import pytest
from sqlalchemy.exc import IntegrityError

from app.accounts.daos.user_dao import UserDao
from app.accounts.tests.factories import UserFactory


def test_create_user_ok(session):
    user = UserDao(session=session).create(
        email="myemail", password_hash="myhashedpassword"
    )

    assert user.email == "myemail"
    assert user.password_hash == "myhashedpassword"


def test_create_user_failure_duplicate_email(session):
    user = UserFactory()

    with pytest.raises(IntegrityError) as ctx:
        UserDao(session=session).create(email=user.email, password_hash="hashed")

    assert "users_email_key" in ctx.value.args[0]


def test_query_filter_by_id(session, subtests):
    user_1 = UserFactory()
    user_2 = UserFactory()

    cases = [({}, [user_1, user_2]), ({"id": user_1.id}, [user_1])]

    for filters, expected_users in cases:
        with subtests.test():
            users = UserDao(session=session).list(**filters)
            assert users == expected_users


def test_query_filter_by_email(session, subtests):
    user_1 = UserFactory()
    user_2 = UserFactory()

    cases = [({}, [user_1, user_2]), ({"email": user_1.email}, [user_1])]

    for filters, expected_users in cases:
        with subtests.test():
            users = UserDao(session=session).list(**filters)
            assert users == expected_users
