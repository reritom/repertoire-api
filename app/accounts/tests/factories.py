from factory import (
    Sequence,
    alchemy,
)
from werkzeug.security import generate_password_hash

from app.accounts.models.user import User
from app.accounts.models.user_preference import UserPreference
from app.database import Session

TEST_PASSWORD = "iampassword"


class UserFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    email = Sequence(lambda n: "User{}".format(n))

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        kwargs["password_hash"] = generate_password_hash(TEST_PASSWORD)
        return super()._create(model_class, *args, **kwargs)


class UserPreferenceFactory(alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = UserPreference
        sqlalchemy_session = Session
        sqlalchemy_session_persistence = "flush"

    name = Sequence(lambda n: "UserPreference{}".format(n))
    value = True
