from app.accounts.schemas.user_schema import UserCreationSchema
from app.accounts.services.user_service.service import create_user, get_user
from app.accounts.tests.factories import UserFactory


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
