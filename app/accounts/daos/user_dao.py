from app.accounts.models.user import User
from app.shared.dao import BaseDao
from app.shared.sentinels import NO_FILTER, OptionalFilter


class UserDao(BaseDao[User]):
    class Meta:
        model = User

    def create(self, email: str, password_hash: str) -> User:
        user = User(email=email, password_hash=password_hash)
        with self.session.begin_nested():
            self.session.add(user)
        self.session.flush()
        return user

    def query(
        self,
        id: OptionalFilter[int] = NO_FILTER,
        email: OptionalFilter[str] = NO_FILTER,
    ):
        statement = super().query()

        if id is not NO_FILTER:
            statement = statement.where(User.id == id)

        if email is not NO_FILTER:
            statement = statement.where(User.email == email)

        return statement
