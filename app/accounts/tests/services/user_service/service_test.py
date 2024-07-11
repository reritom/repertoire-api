import pytest

from app.accounts.schemas.user_schema import UserCreationSchema
from app.accounts.services.user_service.service import (
    create_user,
    get_user,
    get_user_from_credentials,
)
from app.accounts.tests.factories import TEST_PASSWORD, UserFactory
from app.shared.exceptions import ServiceValidationError


def test_create_user_ok(session):
    user = create_user(
        session=session,
        user_creation_payload=UserCreationSchema(
            email="myemail", password="mypassword"
        ),
    )

    assert user.email == "myemail"
    assert user.password_hash is not None
    assert user.password_hash != "mypassword"


def test_get_user_ok(session):
    user = UserFactory()

    retrieved = get_user(session=session, user_id=user.id)

    assert retrieved == user


def test_get_user_from_credentials_ok(session):
    user = UserFactory()

    retrieved = get_user_from_credentials(
        session=session, email=user.email, password=TEST_PASSWORD
    )

    assert retrieved == user


def test_get_user_from_credentials_failure_invalid_email(session):
    with pytest.raises(ServiceValidationError) as ctx:
        get_user_from_credentials(
            session=session, email="invalid", password=TEST_PASSWORD
        )

    assert ctx.value.args[0] == "Invalid credentials"


def test_get_user_from_credentials_failure_invalid_password(session):
    user = UserFactory()

    with pytest.raises(ServiceValidationError) as ctx:
        get_user_from_credentials(
            session=session, email=user.email, password="iamthewrongpassword"
        )

    assert ctx.value.args[0] == "Invalid credentials"
