from typer import Option, Typer

from app.accounts.schemas.user_schema import UserCreationSchema
from app.accounts.services.user_service.service import create_user as _create_user
from app.database import using_get_session

app = Typer()


@app.command("create-user")
def create_user(email: str = Option(...), password: str = Option(...)):
    with using_get_session() as session:
        _create_user(
            session=session,
            user_creation_payload=UserCreationSchema(email=email, password=password),
        )
