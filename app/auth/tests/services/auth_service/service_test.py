from datetime import datetime

import pytest

from app.accounts.tests.factories import TEST_PASSWORD, UserFactory
from app.auth.schemas.login_schema import LoginSchema
from app.auth.services.auth_service.service import get_authenticated_user, login_user
from app.shared.exceptions import ServiceValidationError


def test_login_ok(session):
    user = UserFactory()

    token, expires = login_user(
        session=session,
        user_credentials=LoginSchema(email=user.email, password=TEST_PASSWORD),
    )

    # TODO do more precise assertions
    assert token is not None
    assert expires > datetime.utcnow()


def test_login_failure_invalid_credentials(session):
    with pytest.raises(ServiceValidationError) as ctx:
        login_user(
            session=session,
            user_credentials=LoginSchema(email="invalidemail", password=TEST_PASSWORD),
        )

    assert ctx.value.args[0] == "Invalid credentials"


def test_get_authenticated_user_ok(session):
    UserFactory.create_batch(3)
    user = UserFactory()

    access_token, _ = login_user(
        session=session,
        user_credentials=LoginSchema(email=user.email, password=TEST_PASSWORD),
    )

    authenticated_user = get_authenticated_user(
        session=session, access_token=access_token
    )

    assert authenticated_user == user


@pytest.mark.skip("Not written")
def test_get_authenticated_user_failure_invalid_access_token():
    ...
